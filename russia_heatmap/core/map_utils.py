import numpy as np


def format_number(number: int | float | None) -> str:
    if number is None or np.isnan(number):
        return "Отсутствует"
    return f"{int(number):,}".replace(",", " ")


def format_percent(number: float) -> str:
    if number is None or np.isnan(number):
        return "Отсутствует"
    return f"{number * 100 :.2f} %"
