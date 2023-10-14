import difflib
import io

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import uvicorn
from fastapi import FastAPI, Response
from shapely import MultiPolygon
from shapely.affinity import translate
from shapely.geometry import LineString
from shapely.ops import split
from starlette.background import BackgroundTasks

app = FastAPI()
matplotlib.use('agg')


def shift_map(mymap, shift):
    shift -= 180
    moved_map = []
    splitted_map = []
    border = LineString([(shift, 90), (shift, -90)])
    for row in mymap["geometry"]:
        splitted_map.append(split(row, border))
    for element in splitted_map:
        items = list(element.geoms)
        if len(items) == 1:
            item = items[0]
            minx, miny, maxx, maxy = item.bounds
            if minx >= shift:
                moved_map.append(translate(item, xoff=-180 - shift))
            else:
                moved_map.append(translate(item, xoff=180 - shift))
            continue
        multipolygon = []
        for item in items:
            minx, miny, maxx, maxy = item.bounds
            if minx >= shift:
                multipolygon.append(translate(item, xoff=-180 - shift))
            else:
                multipolygon.append(translate(item, xoff=180 - shift))
        moved_map.append(MultiPolygon(multipolygon))
    return moved_map


def get_plot():
    SHAPEFILE = r'F:\Programming\Julya\russia_heatmap\RF\admin_4.shp'
    # Read shapefile using Geopandas
    geo_df = gpd.read_file(SHAPEFILE)[["name_ru", "ref", "geometry"]]

    geo_df['geometry'] = shift_map(geo_df, 100)

    colormap_data = pd.read_csv(r'F:\Programming\Julya\russia_heatmap\RF\colormap.csv')
    colormap_data['Названия строк'] = colormap_data['Названия строк'].replace(
        {
            'Республика Тыва': 'Тыва',
            'Удмуртская Республика': 'Удмуртия',
            'Чеченская Республика': 'Чечня',
            'Чувашская Республика - Чувашия': "Чувашия"
        }
    )
    colormap_data['Процент'] = colormap_data['Процент'].str.replace("%", '').str.replace(',', '.').astype(float)

    target_region_names = list(geo_df['name_ru'])
    colormap_region_names = list(colormap_data['Названия строк'])
    target_region_names.sort()
    colormap_region_names.sort()

    target_map = {target: next(iter(difflib.get_close_matches(target, colormap_region_names, cutoff=0.5)), None) for
                  target in target_region_names}
    geo_df['name_ru'].replace(target_map, inplace=True)
    merged_df = pd.merge(left=geo_df, right=colormap_data, left_on='name_ru', right_on='Названия строк', how="right")

    col = 'Процент'
    source = 'Процент дел (?) по регионам Российской Федерации'
    vmin = merged_df[col].min()
    vmax = merged_df[col].max()
    cmap = 'YlGnBu'

    fig, ax = plt.subplots(1, figsize=(30, 12))
    merged_df.plot(column=col, ax=ax, edgecolor='0.8', linewidth=1, cmap=cmap)
    ax.annotate(source, xy=(0.1, .08), xycoords='figure fraction', horizontalalignment='left',
                verticalalignment='bottom', fontsize=10)
    # Create colorbar as a legend
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
    cbaxes = fig.add_axes([0.85, 0.11, 0.01, 0.77])
    fig.colorbar(sm, cax=cbaxes)

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
