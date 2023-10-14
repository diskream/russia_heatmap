import difflib
import io

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import uvicorn
from fastapi import FastAPI, Response
from geopandas import GeoDataFrame
from shapely import MultiPolygon, Polygon
from shapely.affinity import translate
from shapely.geometry import LineString
from shapely.ops import split
from starlette.background import BackgroundTasks

app = FastAPI()
matplotlib.use('agg')


def translate_geometry(polygon: Polygon, geometry_list: list[Polygon | MultiPolygon], shift: int) -> None:
    """Translates polygon with shift and appends to geometry list.

    :param polygon:
    :param geometry_list:
    :param shift:
    """
    min_x, *_ = polygon.bounds
    if min_x >= shift:
        geometry_list.append(translate(polygon, xoff=-180 - shift))
    else:
        geometry_list.append(translate(polygon, xoff=180 - shift))


def shift_map(geo_dataframe: GeoDataFrame, shift: int) -> list[Polygon | MultiPolygon]:
    """

    :param geo_dataframe:
    :param shift:
    :return:
    """
    shift -= 180
    moved_map: list[Polygon | MultiPolygon] = []
    border = LineString([(shift, 90), (shift, -90)])

    split_map = [split(row, border) for row in geo_dataframe["geometry"]]

    for element in split_map:
        items = list(element.geoms)
        if len(items) == 1:
            translate_geometry(next(iter(items)), moved_map, shift)
            continue

        multipolygon: list[MultiPolygon] = []

        for item in items:
            translate_geometry(item, multipolygon, shift)

        moved_map.append(MultiPolygon(multipolygon))

    return moved_map


def get_data_for_plot() -> pd.DataFrame:
    geo_df = gpd.read_file(r'RF/admin_4.shp')[["name_ru", "ref", "geometry"]]

    geo_df['geometry'] = shift_map(geo_df, 100)

    colormap_data = pd.read_csv(r'RF/colormap.csv')
    colormap_data['Названия строк'] = colormap_data['Названия строк'].replace(
        {
            'Республика Тыва': 'Тыва',
            'Удмуртская Республика': 'Удмуртия',
            'Чеченская Республика': 'Чечня',
            'Чувашская Республика - Чувашия': "Чувашия"
        }
    )

    colormap_data['Процент'] = colormap_data['Процент'].str.replace("%", '').str.replace(',', '.').astype(float)

    target_region_names: list[str] = list(geo_df['name_ru'])
    colormap_region_names: list[str] = list(colormap_data['Названия строк'])
    target_region_names.sort()
    colormap_region_names.sort()

    target_map = {
        target: next(iter(difflib.get_close_matches(target, colormap_region_names, cutoff=0.5)), None)
        for target in target_region_names
    }

    geo_df['name_ru'].replace(target_map, inplace=True)

    return pd.merge(left=geo_df, right=colormap_data, left_on='name_ru', right_on='Названия строк', how="right")


def get_plot():
    df = get_data_for_plot()

    target_colormap_column: str = 'Процент'
    color_map: str = 'YlGnBu'

    fig, ax = plt.subplots(1, figsize=(30, 12))

    df.plot(column=target_colormap_column, ax=ax, edgecolor='0.8', linewidth=1, cmap=color_map)

    ax.annotate(
        'Процент дел (?) по регионам Российской Федерации',
        xy=(0.1, .08),
        xycoords='figure fraction',
        horizontalalignment='left',
        verticalalignment='bottom',
        fontsize=10,
    )

    fig.colorbar(
        plt.cm.ScalarMappable(
            norm=plt.Normalize(
                vmin=df[target_colormap_column].min(),
                vmax=df[target_colormap_column].max(),
            ),
            cmap=color_map,
        ),
        cax=fig.add_axes([0.85, 0.11, 0.01, 0.77]),
    )

    plt.plot()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    plt.close(fig)
    return img_buf


@app.get('/')
def show_plot(background_tasks: BackgroundTasks):
    img_buf = get_plot()
    background_tasks.add_task(img_buf.close)
    headers = {'Content-Disposition': 'inline; filename="out.png"'}
    return Response(img_buf.getvalue(), headers=headers, media_type='image/png')


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
