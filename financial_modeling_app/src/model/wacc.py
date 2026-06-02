"""Weighted-average cost of capital calculations."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WACCResult:
    cost_of_equity: float
    after_tax_cost_of_debt: float
    wacc: float
    debt_to_capital: float
    equity_to_capital: float


def normalize_capital_weights(debt_to_capital: float, equity_to_capital: float) -> tuple[float, float]:
    """Return debt/equity capital weights that sum to 1.0."""
    total = debt_to_capital + equity_to_capital
    if total <= 0:
        raise ValueError("Debt-to-capital plus equity-to-capital must be positive.")
    return debt_to_capital / total, equity_to_capital / total


def calculate_wacc(
    risk_free_rate: float,
    equity_risk_premium: float,
    beta: float,
    pre_tax_cost_of_debt: float,
    tax_rate: float,
    debt_to_capital: float,
    equity_to_capital: float,
) -> WACCResult:
    """Calculate CAPM cost of equity, after-tax cost of debt, and WACC."""
    debt_weight, equity_weight = normalize_capital_weights(debt_to_capital, equity_to_capital)
    cost_of_equity = risk_free_rate + beta * equity_risk_premium
    after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
    wacc = cost_of_equity * equity_weight + after_tax_cost_of_debt * debt_weight
    return WACCResult(cost_of_equity, after_tax_cost_of_debt, wacc, debt_weight, equity_weight)
