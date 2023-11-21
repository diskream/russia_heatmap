import os
import shutil
from tkinter import filedialog
from typing import Literal

from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler
from russia_heatmap.core.utils import resource_path

IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")


@callback(
    Output("open-presentation-directory", "color"),
    Output("open-presentation-directory", "outline"),
    Input("open-presentation-directory", "n_clicks"),
)
def open_presentation_directory_callback(n_clicks: int | None) -> tuple[Literal["success"], Literal[True]]:
    if n_clicks is None:
        raise PreventUpdate
    print("dir asked")
    ask_dir = filedialog.askdirectory()
    print("dir asked")
    map_handler.presentation_dir_path = ask_dir
    presentation_path: str = map_handler.presentation_dir_path

    for file in os.listdir(presentation_path):
        full_file_path: str = os.path.join(presentation_path, file)
        if not os.path.isfile(full_file_path) or not any(file.endswith(ext) for ext in IMAGE_EXTENSIONS):
            continue

        target_file_path: str = os.path.join(resource_path("_temp_slides"), file)
        shutil.copyfile(full_file_path, target_file_path)

    return "success", True
