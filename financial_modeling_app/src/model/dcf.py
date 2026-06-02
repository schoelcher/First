"""Discounted cash flow valuation engine."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

import pandas as pd


@dataclass(frozen=True)
class DCFResult:
    pv_forecast_fcf: float
    terminal_value: float
    pv_terminal_value: float
    enterprise_value: float
    net_debt: float
    equity_value: float
    diluted_shares_outstanding: float
    implied_share_price: float
    current_share_price: float | None
    upside_downside: float | None
    terminal_value_percent_of_ev: float
    wacc: float
    terminal_method: str

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_dcf(
    forecast: pd.DataFrame,
    wacc: float,
    terminal_growth_rate: float,
    exit_ebitda_multiple: float,
    terminal_method: Literal["gordon_growth", "exit_multiple"],
    net_debt: float,
    diluted_shares_outstanding: float,
    current_share_price: float | None = None,
) -> DCFResult:
    """Calculate enterprise value, equity value, and implied share price from forecast FCFs."""
    if forecast.empty or "unlevered_fcf" not in forecast.columns:
        raise ValueError("Forecast must include unlevered_fcf.")
    if not diluted_shares_outstanding or diluted_shares_outstanding <= 0:
        raise ValueError("Diluted shares outstanding must be positive.")
    if wacc <= 0:
        raise ValueError("WACC must be positive.")
    periods = range(1, len(forecast) + 1)
    discounted_fcf = [float(fcf) / ((1 + wacc) ** period) for fcf, period in zip(forecast["unlevered_fcf"], periods)]
    pv_forecast_fcf = float(sum(discounted_fcf))
    final_fcf = float(forecast["unlevered_fcf"].iloc[-1])
    final_ebitda = float(forecast["ebitda"].iloc[-1])
    if terminal_method == "gordon_growth":
        if wacc <= terminal_growth_rate:
            raise ValueError("WACC must be greater than terminal growth rate for Gordon Growth.")
        terminal_value = final_fcf * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    elif terminal_method == "exit_multiple":
        terminal_value = final_ebitda * exit_ebitda_multiple
    else:
        raise ValueError("Unknown terminal method.")
    pv_terminal_value = terminal_value / ((1 + wacc) ** len(forecast))
    enterprise_value = pv_forecast_fcf + pv_terminal_value
    equity_value = enterprise_value - net_debt
    implied_share_price = equity_value / diluted_shares_outstanding
    upside_downside = None if not current_share_price or current_share_price <= 0 else implied_share_price / current_share_price - 1
    terminal_value_percent_of_ev = 0.0 if enterprise_value == 0 else pv_terminal_value / enterprise_value
    return DCFResult(
        pv_forecast_fcf=pv_forecast_fcf,
        terminal_value=float(terminal_value),
        pv_terminal_value=float(pv_terminal_value),
        enterprise_value=float(enterprise_value),
        net_debt=float(net_debt),
        equity_value=float(equity_value),
        diluted_shares_outstanding=float(diluted_shares_outstanding),
        implied_share_price=float(implied_share_price),
        current_share_price=current_share_price,
        upside_downside=float(upside_downside) if upside_downside is not None else None,
        terminal_value_percent_of_ev=float(terminal_value_percent_of_ev),
        wacc=float(wacc),
        terminal_method=terminal_method,
    )
