from typing import Literal

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler


@callback(
    Output("open-presentation-directory", "color"),
    Output("open-presentation-directory", "outline"),
    Output("modal", "is_open"),
    Output("presentation-carousel", "items"),
    Output("modal-header-text", "children"),
    Input("upload-slides", "contents"),
    State("upload-slides", "filename"),
)
def open_presentation_directory_callback(
    images: list[str] | None,
    image_names: list[str] | None,
) -> tuple[Literal["success"], Literal[True]]:
    if images is None:
        raise PreventUpdate

    map_handler.clear_slides()

    carousel_items = []

    for slide_file_name, slide_base64 in zip(image_names, images):
        slide_name, *_ = slide_file_name.split(".")

        map_handler.add_slide(slide_name=slide_name, slide_img=slide_base64)

        carousel_items.append({
            "key": slide_name,
            "src": slide_base64,
            "img_class_name": "carousel-img",
            "img_style": {
                "max-height": "100%",
                "max-width": "100%",
                "width": "auto!important",
                "display": "block",
            }
        })

    return "success", True, True, carousel_items, slide_name
