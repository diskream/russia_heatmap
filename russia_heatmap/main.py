import os
import webbrowser
from threading import Timer

import dash
import dash_bootstrap_components as dbc

from russia_heatmap.callbacks import get_app_layout
from russia_heatmap.core.utils import resource_path

app = dash.Dash(
    __name__,
    assets_folder='assets',
    assets_url_path='/assets',
    serve_locally=True,
    include_assets_files=True,
)

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = get_app_layout()


def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new("http://127.0.0.1:5000/")


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run_server(debug=False, port=5000, threaded=False)
