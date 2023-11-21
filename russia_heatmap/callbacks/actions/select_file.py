import base64

from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core import map_handler


@callback(
    Output("region-column-name", "options"),
    Output("region-column-name", "disabled"),
    Output("target-column-name", "options"),
    Output("target-column-name", "disabled"),
    Input("upload-colormap", "contents"),
)
def select_file_callback(contents: str | None) -> tuple[list[str], bool, list[str], bool]:
    if contents is None:
        raise PreventUpdate
    content_type, content_string = contents.split(",")

    map_handler.colormap_data = base64.b64decode(content_string)

    return map_handler.colormap_columns, False, map_handler.colormap_columns, False
