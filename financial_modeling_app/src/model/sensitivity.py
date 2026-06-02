"""DCF sensitivity table generation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .assumptions import ModelAssumptions
from .dcf import calculate_dcf
from .forecast import generate_forecast


def _label_percent(value: float) -> str:
    return f"{value:.1%}"


def _safe_price(*args, **kwargs) -> float:
    try:
        return calculate_dcf(*args, **kwargs).implied_share_price
    except ValueError:
        return np.nan


def wacc_vs_terminal_growth(forecast: pd.DataFrame, assumptions: ModelAssumptions, base_wacc: float) -> pd.DataFrame:
    """Return implied-price table by WACC and terminal growth."""
    wacc_values = [max(base_wacc + d, 0.001) for d in [-0.01, -0.005, 0.0, 0.005, 0.01]]
    growth_values = [max(assumptions.terminal_growth_rate + d, 0.0) for d in [-0.01, -0.005, 0.0, 0.005, 0.01]]
    data = []
    for wacc in wacc_values:
        data.append([
            _safe_price(forecast, wacc, growth, assumptions.exit_ebitda_multiple, "gordon_growth", assumptions.net_debt, assumptions.diluted_shares_outstanding or 0, assumptions.current_share_price)
            for growth in growth_values
        ])
    return pd.DataFrame(data, index=[_label_percent(v) for v in wacc_values], columns=[_label_percent(v) for v in growth_values])


def wacc_vs_exit_multiple(forecast: pd.DataFrame, assumptions: ModelAssumptions, base_wacc: float) -> pd.DataFrame:
    """Return implied-price table by WACC and exit EBITDA multiple."""
    wacc_values = [max(base_wacc + d, 0.001) for d in [-0.01, -0.005, 0.0, 0.005, 0.01]]
    multiple_values = [max(assumptions.exit_ebitda_multiple + d, 0.1) for d in [-2.0, -1.0, 0.0, 1.0, 2.0]]
    data = []
    for wacc in wacc_values:
        data.append([
            _safe_price(forecast, wacc, assumptions.terminal_growth_rate, multiple, "exit_multiple", assumptions.net_debt, assumptions.diluted_shares_outstanding or 0, assumptions.current_share_price)
            for multiple in multiple_values
        ])
    return pd.DataFrame(data, index=[_label_percent(v) for v in wacc_values], columns=[f"{v:.1f}x" for v in multiple_values])


def revenue_growth_vs_ebitda_margin(historical: pd.DataFrame, assumptions: ModelAssumptions, base_wacc: float) -> pd.DataFrame:
    """Return implied-price table by revenue growth and EBITDA margin."""
    growth_values = [assumptions.revenue_growth + d for d in [-0.02, -0.01, 0.0, 0.01, 0.02]]
    margin_values = [max(assumptions.ebitda_margin + d, -0.50) for d in [-0.04, -0.02, 0.0, 0.02, 0.04]]
    data = []
    for growth in growth_values:
        row = []
        for margin in margin_values:
            scenario = assumptions.model_copy(update={"revenue_growth": growth, "ebitda_margin": margin, "ebit_margin": min(assumptions.ebit_margin, margin)})
            scenario_forecast = generate_forecast(historical, scenario)
            row.append(_safe_price(scenario_forecast, base_wacc, scenario.terminal_growth_rate, scenario.exit_ebitda_multiple, scenario.terminal_method, scenario.net_debt, scenario.diluted_shares_outstanding or 0, scenario.current_share_price))
        data.append(row)
    return pd.DataFrame(data, index=[_label_percent(v) for v in growth_values], columns=[_label_percent(v) for v in margin_values])


def build_sensitivity_tables(historical: pd.DataFrame, forecast: pd.DataFrame, assumptions: ModelAssumptions, base_wacc: float) -> dict[str, pd.DataFrame]:
    return {
        "wacc_terminal_growth": wacc_vs_terminal_growth(forecast, assumptions, base_wacc),
        "wacc_exit_multiple": wacc_vs_exit_multiple(forecast, assumptions, base_wacc),
        "revenue_growth_ebitda_margin": revenue_growth_vs_ebitda_margin(historical, assumptions, base_wacc),
    }
