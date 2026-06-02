"""Formatting helpers for UI and Excel."""
from __future__ import annotations

import math


def _missing(value: float | int | None) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def format_currency(value: float | None, decimals: int = 1) -> str:
    if _missing(value):
        return "—"
    abs_value = abs(float(value))
    sign = "-" if float(value) < 0 else ""
    if abs_value >= 1_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000:.{decimals}f}B"
    if abs_value >= 1_000_000:
        return f"{sign}${abs_value / 1_000_000:.{decimals}f}M"
    if abs_value >= 1_000:
        return f"{sign}${abs_value / 1_000:.{decimals}f}K"
    return f"{sign}${abs_value:.{decimals}f}"


def format_percent(value: float | None, decimals: int = 1) -> str:
    return "—" if _missing(value) else f"{float(value):.{decimals}%}"


def format_multiple(value: float | None, decimals: int = 1) -> str:
    return "—" if _missing(value) else f"{float(value):.{decimals}f}x"


def format_number(value: float | None, decimals: int = 1) -> str:
    return "—" if _missing(value) else f"{float(value):,.{decimals}f}"


def convert_decimal_to_percent_display(value: float | None) -> float:
    return 0.0 if _missing(value) else float(value) * 100
