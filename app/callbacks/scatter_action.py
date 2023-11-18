from dash import Input, Output, callback
from dash.exceptions import PreventUpdate


@callback(
    Output("hidden-div", "n_clicks"),
    Input("main-map", "clickData"),
)
def scatter_action(selected_data):
    if selected_data is None:
        raise PreventUpdate
    return 2
