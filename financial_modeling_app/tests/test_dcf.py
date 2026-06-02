import pandas as pd
import pytest

from src.model.dcf import calculate_dcf


def forecast_df():
    return pd.DataFrame(
        {"unlevered_fcf": [100, 110, 120, 130, 140], "ebitda": [200, 220, 240, 260, 280]},
        index=[2025, 2026, 2027, 2028, 2029],
    )


def test_gordon_growth_terminal_value_and_price():
    result = calculate_dcf(forecast_df(), 0.10, 0.03, 12, "gordon_growth", 50, 10, 100)
    assert result.terminal_value == pytest.approx(140 * 1.03 / (0.10 - 0.03))
    assert result.equity_value == pytest.approx(result.enterprise_value - 50)
    assert result.implied_share_price == pytest.approx(result.equity_value / 10)


def test_exit_multiple_terminal_value():
    result = calculate_dcf(forecast_df(), 0.10, 0.03, 12, "exit_multiple", 0, 10, None)
    assert result.terminal_value == pytest.approx(280 * 12)
    assert result.upside_downside is None


def test_invalid_wacc_growth_raises():
    with pytest.raises(ValueError):
        calculate_dcf(forecast_df(), 0.03, 0.03, 12, "gordon_growth", 0, 10, 100)


def test_invalid_shares_raises():
    with pytest.raises(ValueError):
        calculate_dcf(forecast_df(), 0.10, 0.03, 12, "exit_multiple", 0, 0, 100)
