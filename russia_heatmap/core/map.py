import io
import logging
import os

import geopandas as gpd
import pandas as pd
from plotly.graph_objs import Figure

from russia_heatmap.core.map_of_russia import RussiaHeatMap
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

        self.map: RussiaHeatMap | None = None

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
            self._colormap_data = pd.read_excel(io.BytesIO(value))

    @property
    def colormap_columns(self) -> list[str]:
        return list(self.colormap_data.columns)

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
                "Значение": round(total_declared, 3),
            },
            {
                "Название": "Взыскано",
                "Значение": round(total_recovered, 3),
            },
            {
                "Название": "Процент отбития",
                "Значение": f"{round(((total_declared - total_recovered) / total_declared) * 100, 2)} %",
            },
        ]

    def _get_startup_map(self) -> Figure:
        if self.map is None:
            self.map = RussiaHeatMap(
                gdf=self.gdf,
                region_column_name=self.region_column_name,
                target_column_name=self.target_column_name,
                from_startup=True,
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
        )

        if not_found_regions:
            logger.error(not_found_regions)

        return self.map


map_handler = _MapHandlerSingleton()
