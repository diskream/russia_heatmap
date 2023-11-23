import re
from typing import Any, Literal

from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler

CarouselItems = list[dict[Literal["key", "src", "alt", "img_style"], str]]


@callback(
    Output("modal", "is_open"),
    Output("presentation-carousel", "items"),
    Output("modal-header-text", "children"),
    Output("error-alert", "is_open"),
    Output("error-alert", "children"),
    Input("main-map", "clickData"),
)
def scatter_action(selected_data: dict[str, Any]) -> tuple[bool, CarouselItems, str, bool, str]:
    if selected_data is None:
        raise PreventUpdate

    carousel_items: CarouselItems = []
    found_files: list[str] = []

    curve_number: int = selected_data["points"][0]["curveNumber"]
    try:
        district: str = map_handler.get_district_by_curve_number(curve_number)
    except AttributeError:
        return False, [], "", True, "Для отображения презентации необходимо окрасить карту."

    for slide_name, slide in map_handler.slides.items():
        if slide_name.lower().startswith(district.lower()):
            _district, key, *_ = re.split(r"[_\.]", slide_name)
            carousel_items.append({"key": key, "src": slide, "img_style": {"height": "95vh", "width": "98%"}})
            found_files.append(slide_name)

    if not carousel_items:
        msg = "Для данного РЦСО не найдены слайды. Убедитесь, что слайды названы 'РЦСО№{номер_рцсо}_{номер_слайда}'"
        return False, [], "", True, msg

    return True, sorted(carousel_items, key=lambda row: int(row["key"])), district, False, ""
