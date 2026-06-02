"""Data quality and valuation validation checks."""
from __future__ import annotations

import pandas as pd


def validate_historical_financials(df: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    if df.empty:
        return ["Historical financials are empty."]
    if "revenue" not in df or df["revenue"].isna().any():
        warnings.append("Missing revenue for one or more fiscal years.")
    if "operating_income" not in df or df["operating_income"].isna().any():
        warnings.append("Missing EBIT / operating income for one or more fiscal years.")
    if "diluted_shares_outstanding" not in df or df["diluted_shares_outstanding"].isna().all():
        warnings.append("Missing diluted shares outstanding.")
    if "revenue" in df and (df["revenue"].dropna() < 0).any():
        warnings.append("Negative revenue detected; model may not be appropriate.")
    if "capex" in df and "revenue" in df:
        ratio = (df["capex"].abs() / df["revenue"].replace(0, pd.NA)).dropna()
        if not ratio.empty and (ratio > 0.30).any():
            warnings.append("Extreme capex / revenue detected (>30%).")
    if "operating_income" in df and "depreciation_and_amortization" in df and "revenue" in df:
        ebitda_margin = ((df["operating_income"] + df["depreciation_and_amortization"].fillna(0)) / df["revenue"].replace(0, pd.NA)).dropna()
        if not ebitda_margin.empty and ((ebitda_margin > 0.70) | (ebitda_margin < -0.20)).any():
            warnings.append("Extreme EBITDA margin detected; company may be outside v1 scope.")
    return warnings


def validate_assumptions(wacc: float, terminal_growth_rate: float, debt_to_capital: float, equity_to_capital: float) -> list[str]:
    warnings: list[str] = []
    if wacc <= terminal_growth_rate:
        warnings.append("WACC must exceed terminal growth rate for Gordon Growth valuation.")
    if abs((debt_to_capital + equity_to_capital) - 1.0) > 0.001:
        warnings.append("Debt/capital plus equity/capital does not equal 100%; weights will be normalized.")
    return warnings


def validate_dcf_result(dcf_result: dict) -> list[str]:
    warnings: list[str] = []
    tv_pct = dcf_result.get("terminal_value_percent_of_ev")
    if tv_pct is not None and tv_pct > 0.85:
        warnings.append("Terminal value is above 85% of enterprise value.")
    return warnings


def scope_warning(ticker: str, company_name: str) -> list[str]:
    text = f"{ticker} {company_name}".lower()
    excluded = ["bank", "bancorp", "insurance", "reit", "real estate investment trust", "bdc", "biotech", "therapeutics"]
    if any(term in text for term in excluded):
        return ["This company may be a bank, insurer, REIT, BDC, biotech, or other excluded v1 category; model will still attempt to run."]
    return []
