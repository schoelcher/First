import pandas as pd
import pytest

from src.model.assumptions import ModelAssumptions
from src.model.forecast import generate_forecast


def test_forecast_revenue_ebit_and_fcf():
    historical = pd.DataFrame(
        {"revenue": [1000], "operating_working_capital": [100]},
        index=[2024],
    )
    assumptions = ModelAssumptions(
        forecast_years=1,
        revenue_growth=0.10,
        ebit_margin=0.20,
        ebitda_margin=0.25,
        da_percent_revenue=0.03,
        capex_percent_revenue=0.04,
        nwc_percent_revenue=0.12,
        tax_rate=0.21,
        diluted_shares_outstanding=10,
    )
    forecast = generate_forecast(historical, assumptions)
    row = forecast.iloc[0]
    assert row["revenue"] == pytest.approx(1100)
    assert row["ebit"] == pytest.approx(220)
    assert row["ebit_margin"] == pytest.approx(0.20)
    expected_fcf = 220 * (1 - 0.21) + 1100 * 0.03 - 1100 * 0.04 - (1100 * 0.12 - 100)
    assert row["unlevered_fcf"] == pytest.approx(expected_fcf)
