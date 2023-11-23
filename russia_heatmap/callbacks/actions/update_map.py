import logging

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from russia_heatmap.core.map import map_handler

logger = logging.getLogger("update_map_callback")


@callback(
    Output("main-map", "figure"),
    Output("info-table", "data"),
    Output("error-alert-update-map", "is_open"),
    Output("error-alert-update-map", "children"),
    Input("print-map-btn", "n_clicks"),
    State("region-column-name", "value"),
    State("target-column-name", "value"),
)
def update_map_callback(_n_clicks, region_column_name: str | None, target_column_name: str | None):
    if not all((region_column_name, target_column_name)):
        raise PreventUpdate

    map_handler.target_column_name = target_column_name
    map_handler.region_column_name = region_column_name
    try:
        return map_handler.get_map(), map_handler.get_totals_serialized(), False, None
    except Exception as exc:
        logger.error("update_map_callback error: {}".format(exc))
        map_handler.reset_column_names()
        return map_handler.get_map(from_startup=True), None, True, f"При обновлении карты произошла ошибка: {exc}"
