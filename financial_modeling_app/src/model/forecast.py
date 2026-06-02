"""Operating forecast engine."""
from __future__ import annotations

import pandas as pd

from .assumptions import ModelAssumptions


def generate_forecast(historical: pd.DataFrame, assumptions: ModelAssumptions) -> pd.DataFrame:
    """Generate a forecast model using the latest historical year as the base."""
    if historical.empty or "revenue" not in historical.columns:
        raise ValueError("Historical financials must include revenue.")
    base_year = int(historical.index[-1])
    base_revenue = float(historical.iloc[-1]["revenue"])
    base_nwc = float(historical.iloc[-1].get("operating_working_capital", base_revenue * assumptions.nwc_percent_revenue) or 0.0)
    rows = []
    prior_revenue = base_revenue
    prior_nwc = base_nwc
    for year in range(base_year + 1, base_year + assumptions.forecast_years + 1):
        revenue = prior_revenue * (1 + assumptions.revenue_growth)
        ebit = revenue * assumptions.ebit_margin
        ebitda = revenue * assumptions.ebitda_margin
        da = revenue * assumptions.da_percent_revenue
        capex = revenue * assumptions.capex_percent_revenue
        nwc = revenue * assumptions.nwc_percent_revenue
        change_in_nwc = nwc - prior_nwc
        nopat = ebit * (1 - assumptions.tax_rate)
        unlevered_fcf = nopat + da - capex - change_in_nwc
        rows.append(
            {
                "fiscal_year": year,
                "revenue": revenue,
                "revenue_growth": assumptions.revenue_growth,
                "ebit": ebit,
                "ebit_margin": assumptions.ebit_margin,
                "ebitda": ebitda,
                "ebitda_margin": assumptions.ebitda_margin,
                "depreciation_and_amortization": da,
                "capex": capex,
                "operating_working_capital": nwc,
                "change_in_nwc": change_in_nwc,
                "tax_rate": assumptions.tax_rate,
                "nopat": nopat,
                "unlevered_fcf": unlevered_fcf,
            }
        )
        prior_revenue = revenue
        prior_nwc = nwc
    return pd.DataFrame(rows).set_index("fiscal_year")
