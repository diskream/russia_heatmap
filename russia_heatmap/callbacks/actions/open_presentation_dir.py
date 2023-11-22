from typing import Literal

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler


@callback(
    Output("open-presentation-directory", "color"),
    Output("open-presentation-directory", "outline"),
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

    for slide_file_name, slide_base64 in zip(image_names, images):
        slide_name, *_ = slide_file_name.split(".")

        map_handler.add_slide(slide_name=slide_name, slide_img=slide_base64)

    return "success", True
