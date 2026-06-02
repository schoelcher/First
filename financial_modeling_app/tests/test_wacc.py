import pytest

from src.model.wacc import calculate_wacc


def test_wacc_formulas():
    result = calculate_wacc(0.04, 0.05, 1.2, 0.06, 0.21, 0.25, 0.75)
    assert result.cost_of_equity == pytest.approx(0.10)
    assert result.after_tax_cost_of_debt == pytest.approx(0.0474)
    assert result.wacc == pytest.approx(0.10 * 0.75 + 0.0474 * 0.25)


def test_wacc_normalizes_weights():
    result = calculate_wacc(0.04, 0.05, 1.0, 0.06, 0.20, 20, 80)
    assert result.debt_to_capital == pytest.approx(0.20)
    assert result.equity_to_capital == pytest.approx(0.80)
