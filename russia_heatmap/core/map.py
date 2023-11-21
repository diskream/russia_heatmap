import io
import logging
import os
from collections import defaultdict

import geopandas as gpd
import pandas as pd
from plotly.graph_objs import Figure

from russia_heatmap.core.map_of_russia import RussiaHeatMap
from russia_heatmap.core.map_utils import format_number, format_percent
from russia_heatmap.core.utils import compile_gdf, resource_path

logger = logging.getLogger("DialogFrame")
logger.setLevel("INFO")


class _MapHandlerSingleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(_MapHandlerSingleton, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        compiled_gdf_path: str = resource_path(os.path.join("map_data", "russia_regions.parquet"))
        try:
            logger.error("Trying to load parquet {path}".format(path=compiled_gdf_path))
            gdf = gpd.read_parquet(compiled_gdf_path)
        except Exception as exc:
            logger.error("Unable to load parquet {exc}; recompiling gdf...".format(exc=exc))
            gdf = compile_gdf(compiled_gdf_path)

        self.gdf: gpd.GeoDataFrame = gdf
        self.target_column_name: str = ""
        self.region_column_name: str = "region"

        self._colormap_data: pd.DataFrame

        self._district_map: dict[str, set[int]] = defaultdict(set)

        self.map: RussiaHeatMap | None = None

        self._presentation_dir_path: str

    @property
    def colormap_data(self) -> pd.DataFrame:
        if hasattr(self, "_colormap_data"):
            return self._colormap_data
        raise AttributeError("Attribute colormap_data is not set")

    @colormap_data.setter
    def colormap_data(self, value: bytes | pd.DataFrame) -> None:
        if isinstance(value, pd.DataFrame):
            self._colormap_data = value
        else:
            # noinspection PyAttributeOutsideInit
            self._colormap_data = pd.read_excel(io.BytesIO(value))

    @property
    def presentation_dir_path(self) -> str:
        if hasattr(self, "_presentation_dir_path"):
            return self._presentation_dir_path
        raise AttributeError("Attribute presentation_dir_path is not set")

    @presentation_dir_path.setter
    def presentation_dir_path(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Directory path must be string.")
        # noinspection PyAttributeOutsideInit
        self._presentation_dir_path = value

    @property
    def colormap_columns(self) -> list[str]:
        return list(self.colormap_data.columns)

    def get_district_by_curve_number(self, curve_number: int) -> str:
        #'Дальневосточный, Сибирский, Уральский, Северо-Западный, Приволжский, Южный, Центральный, Северо-Кавказский, Крымский'
        if not self._district_map:
            raise AttributeError("District map is not set yet.")
        for district, curve_set in self._district_map.items():
            if curve_number in curve_set:
                return district
        raise KeyError("Curve {} was not found in districts".format(curve_number))

    def get_map(self, *, from_startup: bool = False) -> Figure:
        if from_startup:
            return self._get_startup_map()
        return self._get_map()

    def get_totals_serialized(self) -> list[dict[str, float | str]]:
        try:
            total_declared = self.colormap_data["Заявлено"].sum()
            total_recovered = self.colormap_data["Взыскано"].sum()
        except KeyError:
            return []
        return [
            {
                "Название": "Заявлено",
                "Значение": format_number(total_declared),
            },
            {
                "Название": "Взыскано",
                "Значение": format_number(total_recovered),
            },
            {
                "Название": "Процент отбития",
                "Значение": format_percent((total_declared - total_recovered) / total_declared),
            },
        ]

    def _get_startup_map(self) -> Figure:
        if self.map is None:
            self.map = RussiaHeatMap(
                gdf=self.gdf,
                region_column_name=self.region_column_name,
                target_column_name=self.target_column_name,
                from_startup=True,
                district_map=self._district_map,
            )
        return self.map

    def _get_map(self) -> Figure:
        new_df = pd.merge(
            left=self.gdf, right=self.colormap_data, left_on="region", right_on=self.region_column_name, how="outer"
        )

        not_found_regions: list[str] = list(new_df[new_df["region"].isna()][self.region_column_name])

        new_df.loc[new_df.region == "Севастополь", self.target_column_name] = new_df.loc[
            new_df.region == "Республика Крым", self.target_column_name
        ]
        del self.map
        self.map = RussiaHeatMap(
            gdf=new_df.dropna(subset=["region"]),
            region_column_name=self.region_column_name,
            target_column_name=self.target_column_name,
            district_map=self._district_map,
        )

        if not_found_regions:
            logger.error(not_found_regions)

        return self.map


map_handler = _MapHandlerSingleton()
