import logging
import os

from dash import Dash, html, dcc
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

    return RussiaHeatMap(gdf, from_startup=True)

def setup_app_layout(app: Dash):
    app.layout = html.Div([
        html.Div(children=[html.H1()]),
        dcc.Graph(figure=get_heatmap(), style={'height': '100vh', 'weight': '100vh'})
    ],)