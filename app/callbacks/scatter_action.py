from dash import callback, Output, Input
from dash.exceptions import PreventUpdate

from app.core.map import map_handler


@callback(
    Output("hidden-div", "n_clicks"),
    Input("main-map", "clickData"),
)
def scatter_actiona(selected_data):
    if selected_data is None:
        raise PreventUpdate

    print(selected_data['points'][0]['curveNumber'])
    print(map_handler.map['data'][selected_data['points'][0]['curveNumber']]['name'])
    return 2
