import re
from os import listdir, path
from typing import Literal

from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler

CarouselItems = list[dict[Literal["key", "src"], str]]
IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")


class NoSlideFound(Exception):
    """No slides were found."""


@callback(
    Output("modal", "is_open"),
    Output("presentation-carousel", "items"),
    Input("main-map", "clickData"),
)
def scatter_action(selected_data) -> tuple[Literal[True], CarouselItems]:
    if selected_data is None:
        raise PreventUpdate

    carousel_items: CarouselItems = []

    curve_number: int = selected_data["points"][0]["curveNumber"]
    district: str = map_handler.get_district_by_curve_number(curve_number).lower()
    presentation_path: str = map_handler.presentation_dir_path

    for file in listdir(presentation_path):
        full_file_path: str = path.join(presentation_path, file)
        if not path.isfile(full_file_path) or not any(file.endswith(ext) for ext in IMAGE_EXTENSIONS):
            continue

        if file.lower().startswith(district):
            _district, key, *_ = re.split("_|,", file)
            carousel_items.append({"key": key, "src": full_file_path})
    if not carousel_items:
        raise NoSlideFound("No slides were found.")

    return True, carousel_items
