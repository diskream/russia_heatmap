import logging
import os

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import geopandas as gpd

from app.core.map_of_russia import RussiaHeatMap
from app.core.utils import resource_path, compile_gdf

logger = logging.getLogger("startup")
logger.setLevel("INFO")


def get_heatmap():
    compiled_gdf_path = resource_path(os.path.join("map_data", "russia_regions.parquet"))
    try:
        logger.error("Trying to load parquet {path}".format(path=compiled_gdf_path))
        gdf = gpd.read_parquet(compiled_gdf_path)
    except Exception as exc:
        logger.error("Unable to load parquet {exc}; recompiling gdf...".format(exc=exc))
        gdf = compile_gdf(compiled_gdf_path)

    return RussiaHeatMap(gdf=gdf, target_column_name="", region_column_name="region", from_startup=True)


def setup_app_layout(app: Dash):
    app.layout = html.Div(
        [
            dbc.Row(
                html.H1(
                    "Тепловая карта Российской Федерации",
                    style={"textAlign": "center", "font-family": "Jost"},
                    className="mb-3",
                )
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Label("Выберите .xlsx файл:"), width={"offset": 1}, lg=1),
                    dbc.Col(dbc.Button("Выбрать", id="get-file", n_clicks=0, className="ms-3"), width="auto"),
                    dbc.Col(
                        dcc.Dropdown(
                            id="region-column-name",
                            placeholder="Выберите колонку с названиями регионов",
                            disabled=True,
                        ),
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="target-column-name",
                            placeholder="Выберите целевую колонку",
                            disabled=True,
                        ),
                    ),
                    dbc.Col(
                        dbc.Button("Окрасить карту", id="print-map", className="ms-1", outline=True, color="primary")
                    ),
                ]
            ),
            dcc.Graph(figure=get_heatmap(), style={"height": "100vh", "weight": "100vh"}, id="main-map"),
        ],
        style={"height": "100vh", "weight": "100vh"},
    )
