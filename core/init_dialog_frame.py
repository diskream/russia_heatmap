import difflib
import logging
import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter.ttk import Button, Frame, Label

import geopandas as gpd
import pandas as pd
import typing_extensions

from core.map_of_russia import RussiaHeatMap
from core.utils import compile_gdf

if typing_extensions.TYPE_CHECKING:
    from main import App

logger = logging.getLogger("DialogFrame")


class DialogFrame(Frame):
    def __init__(self, master: "App", compiled_gdf_path: str = "map_data/russia_regions.parquet"):
        Frame.__init__(self, master)

        Label(self, text="Выберите .xlsx файл.").pack(side=tk.LEFT, padx=50, pady=5)

        Button(self, text="Выбрать", command=self._get_xlsx_path_from_explorer).pack(side=tk.LEFT, padx=2, pady=5)

        try:
            logger.info("Trying to load parquet {path}".format(path=compiled_gdf_path))
            gdf = gpd.read_parquet(compiled_gdf_path)
        except Exception as exc:
            logger.error("Unable to load parquet {exc}; recompiling gdf...".format(exc=exc))
            gdf = compile_gdf(compiled_gdf_path)

        self.gdf: gpd.GeoDataFrame = gdf

    def _get_heatmap_plot(self, path_to_colormap_xlsx: str):
        colormap_data = pd.read_excel(path_to_colormap_xlsx)

        target_region_names: list[str] = list(self.gdf["region"])
        colormap_region_names: list[str] = list(colormap_data["Названия строк"])
        target_region_names.sort()
        colormap_region_names.sort()

        target_map: dict[str, str] = {
            target: next(iter(difflib.get_close_matches(target, colormap_region_names, cutoff=0.5)), None)
            for target in target_region_names
        }
        target_map["Севастополь"] = "Севастополь"
        #
        self.gdf["region"].replace(target_map, inplace=True)

        new_df = pd.merge(
            left=self.gdf, right=colormap_data, left_on="region", right_on="Названия строк", how="outer"
        ).dropna()

        # TODO
        new_df.loc[new_df.region == "Севастополь", "Процент"] = new_df.loc[
            new_df.region == "Республика Крым", "Процент"
        ]

        heatmap = RussiaHeatMap(gdf=new_df)

        heatmap.update_layout(showlegend=False, dragmode="pan")
        heatmap.show()

    def _get_xlsx_path_from_explorer(self):
        file = askopenfile(mode="r")
        self._get_heatmap_plot(file.name)
