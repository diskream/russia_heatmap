from typing import Any

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
    "Архангельская область": {
        "shift": {
            "x": 0,
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

    def __init__(self, gdf, add_region_number: bool = True, **kwargs):
        super().__init__(**kwargs)

        unique_percent: set[float] = set(gdf["Процент"])

        red_blue = get_color_range(self.COLOR_MAP, len(unique_percent), mode="rgba")

        # сопоставляем отсортированные значения процентов с rgba цветом
        colormap = dict(zip(sorted(unique_percent), tuple(red_blue)))

        for _, row in gdf.iterrows():
            region_name: str = row["Названия строк"]
            text = f'<b>{region_name}</b><br>Процент отбития: {row["Процент"] * 100 :.2f}%<br>'
            self.add_trace(
                Scatter(
                    x=row.x,
                    y=row.y,
                    name=row.region,
                    text=text,
                    hoverinfo="text",
                    line_color="black",
                    fill="toself",
                    line_width=1,
                    fillcolor=colormap[row["Процент"]][1],
                )
            )
            if add_region_number:
                centroid = row.geometry.centroid
                x, y = centroid.x, centroid.y
                if region_name in REGION_CONFIG:
                    x += REGION_CONFIG[region_name]["shift"]["x"]
                    y += REGION_CONFIG[region_name]["shift"]["y"]
                self.add_trace(
                    Scatter(
                        x=[x],
                        y=[y],
                        text=int(row["Код субъекта РФ"]),
                        mode="text",
                        textposition="middle center",
                    ),
                )
            self.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")

        colorbar_trace = Scatter(
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
                    ticktext=[min(unique_percent), max(unique_percent)],
                    outlinewidth=0,
                ),
            ),
            hoverinfo="none",
        )

        self.add_trace(colorbar_trace)

        # не отображать оси, уравнять масштаб по осям
        self.update_xaxes(visible=False)
        self.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)

        self.update_layout(showlegend=False, dragmode="pan")
