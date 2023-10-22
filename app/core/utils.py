import logging
import os
import sys
from typing import Literal, TypeVar

import geopandas as gpd
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from shapely import MultiPolygon, Polygon
from shapely.geometry.base import GeometrySequence
from shapely.ops import snap, unary_union
from tqdm import tqdm

logger = logging.getLogger("utils")

GDF = TypeVar("GDF", bound=gpd.GeoDataFrame)


def fix_yamalo_nenestky_ao(gdf: GDF) -> GDF:
    """Исправление линии на 180 меридиане Чукотского АО.

    :param gdf:
    :return:
    """
    polygons: list[Polygon] = []
    geoms: GeometrySequence = gdf.loc[gdf.region == "Чукотский автономный округ", "geometry"].values[0].geoms

    for polygon in geoms:
        polygons.extend([snap(polygon, geoms[idx], 100) for idx, _ in enumerate(geoms)])

    gdf.loc[gdf.region == "Чукотский автономный округ", "geometry"] = unary_union(MultiPolygon(polygons))

    return gdf


def prepare_regions(
    gdf: gpd.GeoDataFrame, area_threshold: int = 100e6, simplify_tolerance: int = 500
) -> gpd.GeoDataFrame:
    """Подготовка регионов к построению

    - Упрощение геометрии с допуском simplify_tol
    - Удаление полигонов с площадью менее area_thr
    """
    gdf_ = gdf.copy()

    # Вспомогательный столбец для упорядочивания регионов по площади
    gdf_["area"] = gdf_.geometry.apply(lambda x: x.area)

    # Удаляем маленькие полигоны
    tqdm.pandas(desc="Удаление мелких полигонов")
    gdf_.geometry = gdf_.geometry.progress_apply(
        lambda geometry: MultiPolygon([p for p in geometry.geoms if p.area > area_threshold])
        if type(geometry) == MultiPolygon
        else geometry
    )

    # Упрощение геометрии
    gdf_.geometry = gdf_.geometry.simplify(simplify_tolerance)

    geoms = gdf_.geometry.values
    pbar = tqdm(enumerate(geoms), total=len(geoms))
    pbar.set_description_str("Объединение границ после упрощения")
    # проходим по всем граничащим полигонам и объединяем границы
    for i, g in pbar:
        g1 = g
        for g2 in geoms:
            if g1.distance(g2) < 100:
                g1 = snap(g1, g2, 800)
        geoms[i] = g1
    gdf_.geometry = geoms

    # сортировка по площади
    gdf_ = gdf_.sort_values(by="area", ascending=False).reset_index(drop=True)

    return gdf_.drop(columns=["area"])


def geom_to_shape(g):
    """Преобразование полигонов и мультиполигонов в plotly-readable шэйпы

    Получает на вход Polygon или MultiPolygon из geopandas,
    возвращает pd.Series с координатами x и y
    """
    # Если мультиполигон, то преобразуем каждый полигон отдельно, разделяя их None'ами
    if type(g) == MultiPolygon:
        x, y = np.array([[], []])
        for poly in g.geoms:
            x_, y_ = poly.exterior.coords.xy
            x, y = (np.append(x, x_), np.append(y, y_))
            x, y = (np.append(x, None), np.append(y, None))
        x, y = x[:-1], y[:-1]
    # Если полигон, то просто извлекаем координаты
    elif type(g) == Polygon:
        x, y = np.array(g.exterior.coords.xy)
    # Если что-то другое, то возвращаем пустые массивы
    else:
        x, y = np.array([[], []])
    return pd.Series([x, y])


def compile_gdf(path: str, mode: Literal["pickle", "parquet"] = "parquet") -> gpd.GeoDataFrame:
    """Обработка geojson карты РФ.

    :param path:
    :param mode:
    :return:
    """
    gdf = gpd.read_file(resource_path(os.path.join("map_data", "russia_regions.geojson")))

    # переводим в другой CRS правильного отображения на графике
    gdf.to_crs("ESRI:102027", inplace=True)

    gdf = fix_yamalo_nenestky_ao(gdf)

    gdf = prepare_regions(gdf)

    # добавляем координаты для постройки ScatterPlot
    gdf[["x", "y"]] = gdf.geometry.progress_apply(geom_to_shape)

    gdf = pd.merge(
        left=gdf,
        right=pd.read_excel(resource_path(os.path.join("map_data", "additional_data.xlsx"))),
        left_on="region",
        right_on="Регион",
        how="left",
    )

    # сохраняем обработанный файл, чтобы не тратить время в следующий раз на обработку
    if mode == "pickle":
        gdf.to_pickle(path)
    else:
        gdf.to_parquet(path)

    return gdf


def get_color_range(colormap: LinearSegmentedColormap, color_range: int, mode: Literal["rgb", "rgba"] = "rgb"):
    """Получение списка из RGBA значений, соответствующих градиенту цветов из colormap.

    :param colormap:
    :param color_range:
    :param mode:
    :return:
    """
    h: float = 1.0 / (color_range - 1)
    colorscale: list[list[float | str]] = []

    for alpha in range(color_range):
        color = list(map(np.uint8, np.array(colormap(alpha * h)[:3]) * 255))
        rgb_a_tuple: tuple[float, ...] = tuple(*color) if mode == "rgb" else (*color, 0.9)
        colorscale.append([alpha * h, mode + str(rgb_a_tuple)])

    return colorscale


def resource_path(relative: str) -> str:
    """Получение безопасного пути до ресурса для PyInstaller.

    :param relative:
    :return:
    """
    logger.error(relative)
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)
