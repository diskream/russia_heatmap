import difflib

import geopandas as gpd
import pandas as pd
from geopandas import GeoDataFrame
from shapely import MultiPolygon, Polygon
from shapely.affinity import translate
from shapely.geometry import LineString
from shapely.ops import split


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


def get_data_for_plot(local_data_file_path: str) -> pd.DataFrame:
    geo_df = gpd.read_file(r"RF/admin_4.shp")[["name_ru", "ref", "geometry"]]

    polygons = []
    for idx, polygon in enumerate(geo_df.loc[23]["geometry"].geoms):
        if idx not in {0, 2, 3}:
            polygons.append(polygon)
            continue
        polygons.append(translate(polygon, xoff=300 + 60))

    geo_df["geometry"][23] = MultiPolygon(polygons)

    colormap_data = pd.read_excel(local_data_file_path)
    colormap_data["Названия строк"] = colormap_data["Названия строк"].replace(
        {
            "Республика Тыва": "Тыва",
            "Удмуртская Республика": "Удмуртия",
            "Чеченская Республика": "Чечня",
            "Чувашская Республика - Чувашия": "Чувашия"
        }
    )


    target_region_names: list[str] = list(geo_df["name_ru"])
    colormap_region_names: list[str] = list(colormap_data["Названия строк"])
    target_region_names.sort()
    colormap_region_names.sort()

    target_map = {
        target: next(iter(difflib.get_close_matches(target, colormap_region_names, cutoff=0.5)), None)
        for target in target_region_names
    }

    geo_df["name_ru"].replace(target_map, inplace=True)

    return pd.merge(left=geo_df, right=colormap_data, left_on="name_ru", right_on="Названия строк", how="right")
