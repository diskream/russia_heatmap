from typing import Any

import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from plotly.graph_objects import Figure, Scatter

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

    COLOR_MAP = LinearSegmentedColormap(
        "RedBlue",
        {
            "red": ((0.0, 0.12, 0.12), (1.0, 0.96, 0.96)),
            "green": ((0.0, 0.53, 0.53), (1.0, 0.15, 0.15)),
            "blue": ((0.0, 0.90, 0.90), (1.0, 0.34, 0.34)),
            "alpha": ((0.0, 1, 1), (0.5, 1, 1), (1.0, 1, 1)),
        },
    )
    REGION_NAME_COLUMN: str = "Названия строк"
    TARGET_PERCENT_COLUMN: str = "Процент"

    def __init__(self, gdf, add_region_number: bool = True, **kwargs):
        super().__init__(**kwargs)

        unique_percent: set[float] = set(gdf[self.TARGET_PERCENT_COLUMN])

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

    @classmethod
    def _get_hover_text(cls, row: pd.Series) -> str:
        hover_text: list[str] = []
        for name, value in row.loc[cls.REGION_NAME_COLUMN :].items():
            hover_text.append(
                f"{name}: {value}" if name != cls.TARGET_PERCENT_COLUMN else f"{name}: {value * 100 :.2f} %"
            )
        return "<br>".join(hover_text)

    def _fill_regions(self, row: pd.Series, colormap: dict[float, tuple[float, str]], add_region_number: bool) -> None:
        text = self._get_hover_text(row)
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
                fillcolor=colormap[row[self.TARGET_PERCENT_COLUMN]][1],
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
        region_name: str = row[self.REGION_NAME_COLUMN]
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
