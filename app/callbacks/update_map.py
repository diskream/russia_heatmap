from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from app.core.map import map_handler


@callback(
    Output("main-map", "figure"),
    # Output('info-table', 'data'),
    Input("print-map-btn", "n_clicks"),
    State("region-column-name", "value"),
    State("target-column-name", "value"),
)
def update_map_callback(_n_clicks, region_column_name: str | None, target_column_name: str | None):
    if not all((region_column_name, target_column_name)):
        raise PreventUpdate

    map_handler.target_column_name = target_column_name
    map_handler.region_column_name = region_column_name

    return map_handler.get_map() #, map_handler.get_totals_serialized()
