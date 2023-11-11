from typing import Any

import numpy as np
import pandas as pd
from plotly.graph_objects import Figure, Scatter

from app.core.colormap import LinearColormap
from app.core.utils import get_color_range

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
            **kwargs,
    ):
        super().__init__(**kwargs)

        self._region_column_name = region_column_name
        self._target_column_name = target_column_name

        unique_percent: set[float] = set(gdf[self._target_column_name])

        red_blue = get_color_range(self.COLOR_MAP, len(unique_percent), mode="rgba")

        # сопоставляем отсортированные значения процентов с rgba цветом
        colormap = dict(zip(sorted(unique_percent), tuple(red_blue)))

        for _, row in gdf.iterrows():
            self._fill_regions(row, colormap, add_region_number)

        self._add_colorbar(unique_percent)

        # не отображать оси, уравнять масштаб по осям
        self.update_xaxes(visible=False)
        self.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)

        self.update_layout(showlegend=False, dragmode="pan")

    def _get_hover_text(self, row: pd.Series) -> str:
        hover_text: list[str] = []
        for name, value in row.loc[self._region_column_name :].items():
            if isinstance(value, float) and np.isnan(value):
                hover_text.append(f"{name}: {row['region']}")
                break
            hover_text.append(
                f"{name}: {value * 100 :.2f} %" if 'процент' in name.lower() and isinstance(value, (float, int)) else f"{name}: {value}"
            )
        return "<br>".join(hover_text)

    def _fill_regions(self, row: pd.Series, colormap: dict[float, tuple[float, str]], add_region_number: bool) -> None:
        text = self._get_hover_text(row)
        try:
            color = colormap[row[self._target_column_name]][1]
        except KeyError:
            color = 'grey'
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
        if add_region_number:
            self._add_region_number(row)

        self.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")

    def _add_colorbar(self, unique_percent: set[float]) -> None:
        self.add_trace(
            Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(
                    colorscale=get_color_range(self.COLOR_MAP, 255, mode="rgba"),
                    showscale=True,
                    cmin=-5,
                    cmax=5,
                    colorbar=dict(
                        thickness=20,
                        tickvals=[-5, 5],
                        ticktext=[f"{int(min(unique_percent) * 100)} %", f"{int(max(unique_percent) * 100)} %"],
                        outlinewidth=0,
                    ),
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
