import os
from threading import Timer
import webbrowser

import dash
import dash_bootstrap_components as dbc

from app.factory import setup_app_layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

setup_app_layout(app)


def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=5000)
