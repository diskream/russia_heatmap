import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter.ttk import Button, Frame, Label

import matplotlib
import matplotlib.pyplot as plt
import typing_extensions

from core.utils import get_data_for_plot

if typing_extensions.TYPE_CHECKING:
    from main import App


class DialogFrame(Frame):
    def __init__(self, master: "App"):
        Frame.__init__(self, master)

        Label(self, text="Выберите .xlsx файл.").pack(side=tk.LEFT, padx=50, pady=5)

        Button(self, text="Выбрать", command=self._get_xlsx_path_from_explorer).pack(side=tk.LEFT,padx=2, pady=5)

    def _get_plot(self, file_path: str):
        matplotlib.use("TkAgg")

        df = get_data_for_plot(file_path)
        df.dropna(inplace=True)

        target_colormap_column: str = "Процент"
        color_map: str = "YlGnBu"

        fig, ax = plt.subplots(1, figsize=(30, 12))

        df.plot(column=target_colormap_column, ax=ax, edgecolor="0.8", linewidth=1, cmap=color_map)

        df.apply(lambda x: ax.annotate(text=x["Названия строк"], xy=x.geometry.centroid.coords[0], ha='center'), axis=1)

        ax.annotate(
            "Процент дел (?) по регионам Российской Федерации",
            xy=(0.1, .08),
            xycoords="figure fraction",
            horizontalalignment="left",
            verticalalignment="bottom",
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

        plt.show()

    def _get_xlsx_path_from_explorer(self):
        file = askopenfile(mode="r")
        self._get_plot(file.name)
