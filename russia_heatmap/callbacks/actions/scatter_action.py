import re
from typing import Any, Literal

from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler

CarouselItems = list[dict[Literal["key", "src", "alt"], str]]


class NoSlideFound(Exception):
    """No slides were found."""


@callback(
    Output("modal", "is_open"),
    Output("presentation-carousel", "items"),
    Output("modal-header-text", "children"),
    Input("main-map", "clickData"),
)
def scatter_action(selected_data: dict[str, Any]) -> tuple[Literal[True], CarouselItems, str]:
    if selected_data is None:
        raise PreventUpdate

    carousel_items: CarouselItems = []

    curve_number: int = selected_data["points"][0]["curveNumber"]
    district: str = map_handler.get_district_by_curve_number(curve_number)

    for slide_name, slide in map_handler.slides.items():
        if slide_name.lower().startswith(district.lower()):
            _district, key, *_ = re.split(r"[_\.]", slide_name)
            carousel_items.append({"key": key, "src": slide})

    if not carousel_items:
        raise NoSlideFound("No slides were found.")

    return True, carousel_items, district
