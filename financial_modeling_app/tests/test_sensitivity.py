import numpy as np

from src.model.assumptions import ModelAssumptions
from src.model.forecast import generate_forecast
from src.model.normalized_financials import demo_financials
from src.model.sensitivity import build_sensitivity_tables


def test_sensitivity_tables_shape_base_and_numeric():
    historical, _, _ = demo_financials()
    assumptions = ModelAssumptions(diluted_shares_outstanding=472, current_share_price=100, net_debt=375)
    forecast = generate_forecast(historical, assumptions)
    tables = build_sensitivity_tables(historical, forecast, assumptions, 0.09)
    for table in tables.values():
        assert table.shape == (5, 5)
        assert table.map(lambda x: isinstance(x, (int, float, np.floating)) or np.isnan(x)).all().all()
    assert "9.0%" in tables["wacc_terminal_growth"].index
    assert "2.5%" in tables["wacc_terminal_growth"].columns
    assert "12.0x" in tables["wacc_exit_multiple"].columns
