"""Model assumption defaults and validation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np
import pandas as pd

try:  # Prefer Pydantic when installed by requirements.txt.
    from pydantic import BaseModel, field_validator
except ModuleNotFoundError:  # Allows tests to run in minimal offline environments.
    BaseModel = None  # type: ignore[assignment]
    field_validator = None  # type: ignore[assignment]


@dataclass
class _ModelAssumptionsFallback:
    """Dataclass fallback with the same public helpers used by the app."""

    forecast_years: int = 5
    revenue_growth: float = 0.05
    ebit_margin: float = 0.20
    ebitda_margin: float = 0.25
    da_percent_revenue: float = 0.03
    capex_percent_revenue: float = 0.04
    nwc_percent_revenue: float = 0.05
    tax_rate: float = 0.21
    risk_free_rate: float = 0.045
    equity_risk_premium: float = 0.05
    beta: float = 1.0
    pre_tax_cost_of_debt: float = 0.06
    debt_to_capital: float = 0.20
    equity_to_capital: float = 0.80
    terminal_growth_rate: float = 0.025
    exit_ebitda_multiple: float = 12.0
    terminal_method: Literal["gordon_growth", "exit_multiple"] = "gordon_growth"
    current_share_price: float | None = None
    net_debt: float = 0.0
    diluted_shares_outstanding: float | None = None

    def __post_init__(self) -> None:
        if self.forecast_years <= 0:
            raise ValueError("forecast_years must be positive")

    def model_copy(self, update: dict | None = None):
        values = asdict(self)
        values.update(update or {})
        return type(self)(**values)

    def model_dump(self) -> dict:
        return asdict(self)


if BaseModel is not None:
    class ModelAssumptions(BaseModel):
        """Operating and valuation assumptions stored as decimals where applicable."""

        forecast_years: int = 5
        revenue_growth: float = 0.05
        ebit_margin: float = 0.20
        ebitda_margin: float = 0.25
        da_percent_revenue: float = 0.03
        capex_percent_revenue: float = 0.04
        nwc_percent_revenue: float = 0.05
        tax_rate: float = 0.21
        risk_free_rate: float = 0.045
        equity_risk_premium: float = 0.05
        beta: float = 1.0
        pre_tax_cost_of_debt: float = 0.06
        debt_to_capital: float = 0.20
        equity_to_capital: float = 0.80
        terminal_growth_rate: float = 0.025
        exit_ebitda_multiple: float = 12.0
        terminal_method: Literal["gordon_growth", "exit_multiple"] = "gordon_growth"
        current_share_price: float | None = None
        net_debt: float = 0.0
        diluted_shares_outstanding: float | None = None

        @field_validator("forecast_years")
        @classmethod
        def positive_years(cls, value: int) -> int:
            if value <= 0:
                raise ValueError("forecast_years must be positive")
            return value
else:
    ModelAssumptions = _ModelAssumptionsFallback  # type: ignore[misc, assignment]


def _latest_ratio(df: pd.DataFrame, numerator: str, denominator: str, fallback: float) -> float:
    if numerator not in df.columns or denominator not in df.columns:
        return fallback
    valid = df[[numerator, denominator]].replace([np.inf, -np.inf], np.nan).dropna()
    valid = valid[valid[denominator] != 0]
    if valid.empty:
        return fallback
    return float(valid.iloc[-1][numerator] / valid.iloc[-1][denominator])


def _historical_cagr(df: pd.DataFrame, column: str, fallback: float = 0.05) -> float:
    if column not in df.columns or len(df) < 2:
        return fallback
    series = df[column].dropna()
    series = series[series > 0]
    if len(series) < 2:
        return fallback
    years = len(series) - 1
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def build_default_assumptions(
    historical: pd.DataFrame,
    market_data: dict | None = None,
    terminal_method: Literal["gordon_growth", "exit_multiple"] = "gordon_growth",
) -> ModelAssumptions:
    """Create sensible starting assumptions from historical and market data."""
    market_data = market_data or {}
    latest = historical.iloc[-1] if not historical.empty else pd.Series(dtype=float)
    revenue_growth = max(min(_historical_cagr(historical, "revenue", 0.05), 0.20), -0.05)
    ebit_margin = _latest_ratio(historical, "operating_income", "revenue", 0.20)
    da_ratio = _latest_ratio(historical, "depreciation_and_amortization", "revenue", 0.03)
    ebitda_margin = _latest_ratio(
        historical.assign(ebitda=historical.get("operating_income", 0) + historical.get("depreciation_and_amortization", 0)),
        "ebitda",
        "revenue",
        max(ebit_margin + da_ratio, 0.05),
    )
    capex_ratio = abs(_latest_ratio(historical, "capex", "revenue", 0.04))
    nwc_ratio = _latest_ratio(historical, "operating_working_capital", "revenue", 0.05)
    diluted_shares = market_data.get("shares_outstanding") or latest.get("diluted_shares_outstanding")
    cash = market_data.get("cash") if market_data.get("cash") is not None else latest.get("cash_and_equivalents", 0.0)
    debt = market_data.get("total_debt") if market_data.get("total_debt") is not None else latest.get("total_debt", 0.0)
    net_debt = float((debt or 0.0) - (cash or 0.0))
    return ModelAssumptions(
        revenue_growth=revenue_growth,
        ebit_margin=float(ebit_margin),
        ebitda_margin=float(ebitda_margin),
        da_percent_revenue=float(max(da_ratio, 0.0)),
        capex_percent_revenue=float(max(capex_ratio, 0.0)),
        nwc_percent_revenue=float(nwc_ratio),
        beta=float(market_data.get("beta") or 1.0),
        terminal_method=terminal_method,
        current_share_price=market_data.get("current_share_price"),
        net_debt=net_debt,
        diluted_shares_outstanding=float(diluted_shares) if diluted_shares else None,
    )
