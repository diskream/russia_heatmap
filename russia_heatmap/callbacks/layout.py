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
                                    "width": "95%",
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
                                "width": "95%",
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
                                "width": "95%",
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
                                "width": "95%",
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
                style={"height": "89vh", "weight": "100vh"},
                id="main-map",
            ),
            html.Div(id="hidden-div", style={"display": "none"}),
            html.Div(id="presentation-action-div", style={"display": "none"}),
            html.Div(
                [
                    dbc.Modal(
                        [
                            dbc.ModalHeader(
                                dbc.ModalTitle(
                                    id="modal-header-text",
                                    children="Title"
                                ),
                                style={"height": "70px"}
                            ),
                            dbc.ModalBody(
                                id="modal-body-text",
                                children=dbc.Carousel(
                                    items=[],
                                    controls=True,
                                    indicators=True,
                                    id="presentation-carousel",
                                    class_name="carousel-container",
                                ),
                                style={
                                    "height": "calc(100% - 70px)",
                                    "overflow": "hidden",
                                    "padding": 0,
                                    "display": "block",
                                }
                            ),

                        ],
                        id="modal",
                        is_open=False,
                        style={"max-width": "none", 'max-height': '100%', 'overflow': 'hidden'},
                        centered=True,
                        scrollable=False,
                        size='xl',
                        fullscreen=True,
                    ),
                ]
            ),
        ],
        # style={"height": "100vh", "weight": "100vh"},
    )
