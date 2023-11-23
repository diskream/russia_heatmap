import logging

import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from russia_heatmap.core import map_handler

logger = logging.getLogger("startup")
logger.setLevel("INFO")


def get_app_layout():
    return html.Div(
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
                    dbc.Col(
                        dcc.Upload(
                            id="upload-slides",
                            children=dbc.Button(
                                "Открыть слайды",
                                id="open-presentation-directory",
                                outline=False,
                                color="warning",
                                style={
                                    "width": "100%",
                                },
                            ),
                            accept="image/*",
                            multiple=True,
                        ),
                        width=2,
                        style={
                            "padding": "0 0",
                        },
                    ),
                    dbc.Col(
                        dcc.Upload(
                            id="upload-colormap",
                            children=html.Div(["Открыть .xlsx"]),
                            style={
                                "width": "100%",
                                "height": "40px",
                                "lineHeight": "40px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "margin": "10px",
                            },
                            accept=".xlsx",
                        ),
                        width=2,
                        style={
                            "padding": "0 0",
                        },
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="region-column-name",
                            placeholder="Выберите колонку с названиями регионов",
                            disabled=True,
                            style={
                                "width": "100%",
                            },
                        ),
                        width=2,
                        style={
                            "padding": "0 0",
                        },
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="target-column-name",
                            placeholder="Выберите целевую колонку",
                            disabled=True,
                        ),
                        width=2,
                        style={
                            "padding": "0 0",
                        },
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Окрасить карту",
                            id="print-map-btn",
                            className="ms-1",
                            outline=True,
                            color="primary",
                            style={
                                "width": "100%",
                            },
                        ),
                        width=2,
                        style={
                            "padding": "0 0",
                        },
                    ),
                ],
                justify="evenly",
                align="center",
            ),
            dbc.Alert(id="error-alert", is_open=False, dismissable=True, color="danger", duration=10000),
            dbc.Alert(id="error-alert-update-map", is_open=False, dismissable=True, color="danger", duration=10000),
            dbc.Alert(id="error-alert-select-file", is_open=False, dismissable=True, color="danger", duration=10000),
            dbc.Alert(id="error-alert-scatter-action", is_open=False, dismissable=True, color="danger", duration=10000),
            html.Div(
                [
                    dash_table.DataTable(
                        id="info-table",
                        page_size=10,
                        style_header={"display": "none"},
                        style_cell={"textAlign": "left", "padding": "5px"},
                        style_data={
                            "whiteSpace": "normal",
                        },
                    ),
                ],
                style={"zIndex": 200, "position": "absolute", "margin-top": "2%", "margin-left": "2%"},
            ),
            dcc.Graph(
                figure=map_handler.get_map(from_startup=True),
                style={"height": "89vh", "weight": "100vh", "margin": {"b": "20px"}},
                id="main-map",
            ),
            html.Div(id="presentation-action-div", style={"display": "none"}),
            html.Div(
                [
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle(id="modal-header-text", children="Title")),
                            dbc.Carousel(
                                items=[],
                                controls=True,
                                indicators=True,
                                id="presentation-carousel",
                            ),
                        ],
                        size="xl",
                        id="modal",
                        is_open=False,
                        fullscreen=True,
                    ),
                ]
            ),
        ],
    )
