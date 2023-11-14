import difflib
import logging
import os
import tkinter as tk
import traceback
import typing
from tkinter import messagebox
from tkinter.filedialog import askopenfile
from tkinter.ttk import Button, Frame, Label, Combobox

import geopandas as gpd
import pandas as pd
from plotly.io import write_html

from app.core.error_window import TopErrorWindow
from app.core.map_of_russia import RussiaHeatMap
from app.core.utils import compile_gdf, resource_path

if typing.TYPE_CHECKING:
    from app.main import App

logger = logging.getLogger("DialogFrame")
logger.setLevel("INFO")


class DialogFrame(Frame):
    def __init__(
        self,
        master: "App",
        compiled_gdf_path: str = resource_path(os.path.join("map_data", "russia_regions.parquet")),
    ):
        Frame.__init__(self, master)

        Label(self, text="Выберите .xlsx файл.").grid(row=0, column=0, padx=50, pady=10)

        Button(self, text="Выбрать", command=self._get_xlsx_path_from_explorer).grid(row=0, column=1, padx=50, pady=10)

        Label(self, text="Выбор колонок").grid(row=1, column=0, columnspan=2, padx=50, pady=10)

        self.region_label_text: str = "Названия регионов"
        self.target_label_text: str = "Целевая колонка"

        Label(self, text=self.region_label_text).grid(row=2, column=0, padx=50)
        Label(self, text=self.target_label_text).grid(row=2, column=1, padx=50)

        self.region_column_var = tk.StringVar()

        self.region_column_cb = Combobox(self, textvariable=self.region_column_var, state="disabled")
        self.region_column_cb.grid(row=3, column=0, padx=50, pady=10)

        self.target_column_var = tk.StringVar()
        self.target_column_cb = Combobox(self, textvariable=self.target_column_var, state="disabled")
        self.target_column_cb.grid(row=3, column=1, padx=50, pady=10)

        self.show_map_btn = Button(self, text="Показать карту", command=self.show_map, state="disabled")
        self.show_map_btn.grid(row=4, column=0, columnspan=2, padx=50, pady=10)

        try:
            logger.error("Trying to load parquet {path}".format(path=compiled_gdf_path))
            gdf = gpd.read_parquet(compiled_gdf_path)
        except Exception as exc:
            logger.error("Unable to load parquet {exc}; recompiling gdf...".format(exc=exc))
            gdf = compile_gdf(compiled_gdf_path)

        self.gdf: gpd.GeoDataFrame = gdf
        self.colormap_data: pd.DataFrame

    def show_map(self):
        target_column = self.target_column_var.get()
        region_column = self.region_column_var.get()

        if target_column == "" or region_column == "":
            return messagebox.showerror(
                "Не выбраны необходимые колонки",
                f"Для отображения карты необходимо выбрать <{self.region_label_text}> и <{self.target_label_text}>.",
            )

        self._get_heatmap_plot(region_column, target_column)

    def _get_heatmap_plot(self, region_column_name: str, target_column_name: str):
        target_region_names: list[str] = list(self.gdf["region"])
        colormap_region_names: list[str] = list(self.colormap_data[region_column_name])
        target_region_names.sort()
        colormap_region_names.sort()

        target_map: dict[str, str] = {}
        for target in target_region_names:
            colormap_region_name: str | None = next(
                iter(difflib.get_close_matches(target, colormap_region_names, cutoff=0.5)),
                None,
            )
            if colormap_region_name is not None:
                target_map[target] = colormap_region_name
        target_map["Севастополь"] = "Севастополь"
        #
        self.gdf["region"].replace(target_map, inplace=True)

        new_df = pd.merge(
            left=self.gdf, right=self.colormap_data, left_on="region", right_on=region_column_name, how="outer"
        )

        not_found_regions: list[str] = list(new_df[new_df["region"].isna()][region_column_name])

        new_df.loc[new_df.region == "Севастополь", target_column_name] = new_df.loc[
            new_df.region == "Республика Крым", target_column_name
        ]
        try:
            heatmap = RussiaHeatMap(
                gdf=new_df.dropna(subset=["region"]),
                region_column_name=region_column_name,
                target_column_name=target_column_name,
            )
        except Exception as exc:
            msg = "При создании карты произошла ошибка."
            detail = traceback.format_exc()
            TopErrorWindow(
                title="При создании карты произошла ошибка",
                message=msg,
                detail=detail,
                detail_btn_text="Трассировка ошибки",
            )
            raise exc

        if not_found_regions:
            write_html(heatmap, "map.html")
            msg = "Следующие регионы не заполнены или имеют неправильное название:\n\t{}\n Показать карту?".format(
                ",\n\t".join(not_found_regions)
            )
            detail = "\n".join(new_df.dropna(subset=["region"])["region"].sort_values())
            TopErrorWindow(
                title="Найдены незаполненные названия регионов",
                message=msg,
                detail="Скопируйте Ctrl + A и вставьте в Excel\n" + detail,
                ok_callable=heatmap.show,
                detail_btn_text="Показать доступные названия регионов",
            )
            return

        heatmap.show()

    def _get_xlsx_path_from_explorer(self):
        # сбрасываем выбор полей
        self.target_column_cb.set("")
        self.region_column_cb.set("")

        # открываем файл
        file = askopenfile(mode="r")
        self.colormap_data = pd.read_excel(file.name)

        columns: list[str] = list(self.colormap_data.columns)

        # проставляем новые значения в колонки
        self.target_column_cb["values"] = columns
        self.region_column_cb["values"] = columns

        self.target_column_cb["state"] = "enabled"
        self.region_column_cb["state"] = "enabled"
        self.show_map_btn["state"] = "enabled"
