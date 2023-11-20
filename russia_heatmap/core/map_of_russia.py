from typing import Any

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure, Scatter

from russia_heatmap.core.colormap import LinearColormap
from russia_heatmap.core.map_utils import format_number, format_percent
from russia_heatmap.core.utils import get_color_range

REGION_CONFIG: dict[str, dict[str, Any]] = {
    "Московская область": {
        "shift": {
            "x": 0,
            "y": 5e4,
        },
    },
    "Республика Мордовия": {
        "shift": {
            "x": 0,
            "y": -2e4,
        },
    },
    "Астраханская область": {
        "shift": {
            "x": 1e4,
            "y": 0,
        },
    },
    "Краснодарский край": {
        "shift": {
            "x": 0,
            "y": 2e4,
        },
    },
    "Сахалинская область": {
        "shift": {
            "x": -4e4,
            "y": 0,
        },
    },
    "Хабаровский край": {
        "shift": {
            "x": 2e4,
            "y": -2e5,
        },
    },
    "Камчатский край": {
        "shift": {
            "x": 0,
            "y": -2e5,
        },
    },
    "Ненецкий автономный округ": {
        "shift": {
            "x": 0,
            "y": -2e4,
        },
    },
    "Республика Адыгея": {
        "shift": {
            "x": 2e4,
            "y": 0,
        },
    },
}


class RussiaHeatMap(Figure):
    """Шаблон фигуры для рисования поверх карты России"""

    COLOR_MAP = LinearColormap(
        "RedBlue",
        {
            "red": ((0.0, 0.12, 0.12), (1.0, 0.96, 0.96)),
            "green": ((0.0, 0.53, 0.53), (1.0, 0.15, 0.15)),
            "blue": ((0.0, 0.90, 0.90), (1.0, 0.34, 0.34)),
            "alpha": ((0.0, 1, 1), (0.5, 1, 1), (1.0, 1, 1)),
        },
    )

    def __init__(
        self,
        *,
        gdf,
        region_column_name: str,
        target_column_name: str,
        add_region_number: bool = True,
        from_startup: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._region_column_name = region_column_name
        self._target_column_name = target_column_name
        self._from_startup = from_startup

        unique_percent: set[float] = set(gdf[self._target_column_name]) if not self._from_startup else {0.0, 1.0}

        red_blue = get_color_range(self.COLOR_MAP, len(unique_percent), mode="rgba")

        # сопоставляем отсортированные значения процентов с rgba цветом
        colormap = dict(zip(sorted(unique_percent), tuple(red_blue)))

        for _, row in gdf.iterrows():
            self._fill_regions(row, colormap)

        # TODO
        # отдельным циклом добавляем номера регионов, чтобы они помещались на график с curveNumber + 1 от регионов
        if add_region_number and not self._from_startup:
            for _, row in gdf.iterrows():
                self._add_region_number(row)

        self._add_colorbar(from_startup)

        # не отображать оси, уравнять масштаб по осям
        self.update_xaxes(visible=False)
        self.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)

        self.update_layout(
            showlegend=False,
            dragmode="pan",
            clickmode="event",
            margin=dict(l=10, r=0, t=0, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

    def _get_hover_text(self, row: pd.Series) -> str:
        hover_text: list[str] = []
        if self._from_startup:
            return f"Регион: {row[self._region_column_name]}"

        region_name: str = (
            row[self._region_column_name] if not isinstance(row[self._region_column_name], float) else row.region
        )
        # и так сойдет :D
        hover_text.extend(
            (
                f"<b>{region_name}</b>",
                f"Заявлено: {format_number(row['Заявлено'])}",
                f"Взыскано: {format_number(row['Взыскано'])}",
                f"% отбития: {format_percent(row['% отбития'])}",
                f"Количество решений в пользу Общества: {format_percent(row['Количество решений в пользу Общества'])}",
                f"Просроченные задачи: {format_number(row['Просроченные задачи'])}",
            )
        )
        return "<br>".join(hover_text)

    def _fill_regions(self, row: pd.Series, colormap: dict[float, tuple[float, str]]) -> None:
        text = self._get_hover_text(row)
        try:
            color = colormap[row[self._target_column_name]][1]
        except KeyError:
            color = "grey"
        self.add_trace(
            Scatter(
                x=row.x,
                y=row.y,
                name=row.region,
                text=text,
                hoverinfo="text",
                hoverlabel=dict(bgcolor="white"),
                line_color="black",
                fill="toself",
                line_width=1,
                fillcolor=color,
            )
        )

    def _add_colorbar(self, from_startup: bool) -> None:
        self.add_trace(
            Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(
                    colorscale=(
                        get_color_range(self.COLOR_MAP, 255, mode="rgba")
                        if not from_startup
                        else px.colors.sequential.Greys
                    ),
                    showscale=True,
                    cmin=-4,
                    cmax=4,
                    colorbar=dict(thickness=25, tickvals=[-4, 4], ticktext=["0 %", "100 %"], outlinewidth=1, len=0.95),
                ),
                hoverinfo="none",
            )
        )

    def _add_region_number(self, row: pd.Series):
        centroid = row.geometry.centroid
        region_name: str = row[self._region_column_name]
        x, y = centroid.x, centroid.y
        if region_name in REGION_CONFIG:
            x += REGION_CONFIG[region_name]["shift"]["x"]
            y += REGION_CONFIG[region_name]["shift"]["y"]
        if region_name == "Архангельская область":
            for shift in ((-4e5, -3e5), (6e5, 4e5), (1e6, 1.25e6)):
                x_shift, y_shift = shift
                x_shift += x
                y_shift += y
                self._add_region_scatter(x_shift, y_shift, int(row["Код субъекта РФ"]))
            return
        self._add_region_scatter(x, y, int(row["Код субъекта РФ"]))

    def _add_region_scatter(self, x: float, y: float, region_number: int) -> None:
        self.add_trace(
            Scatter(
                x=[x],
                y=[y],
                text=region_number,
                textfont=dict(size=13),
                mode="text",
                textposition="middle center",
                hoverinfo="skip",
            ),
        )
