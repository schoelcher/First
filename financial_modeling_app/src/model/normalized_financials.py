"""Demo and normalization support for historical financials."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "revenue", "gross_profit", "operating_income", "net_income", "tax_expense",
    "depreciation_and_amortization", "capex", "operating_cash_flow", "free_cash_flow",
    "cash_and_equivalents", "total_debt", "current_assets", "current_liabilities",
    "accounts_receivable", "inventory", "accounts_payable", "operating_working_capital",
    "diluted_shares_outstanding", "basic_shares_outstanding",
]


def demo_financials() -> tuple[pd.DataFrame, dict, list[str]]:
    """Return a complete five-year generic public-company demo dataset."""
    data = [
        {"fiscal_year": 2020, "revenue": 10000, "gross_profit": 5200, "operating_income": 1800, "net_income": 1250, "tax_expense": 330, "depreciation_and_amortization": 450, "capex": 520, "operating_cash_flow": 1700, "cash_and_equivalents": 1100, "total_debt": 2600, "current_assets": 3100, "current_liabilities": 1850, "accounts_receivable": 900, "inventory": 700, "accounts_payable": 600, "diluted_shares_outstanding": 500, "basic_shares_outstanding": 490},
        {"fiscal_year": 2021, "revenue": 10800, "gross_profit": 5724, "operating_income": 2052, "net_income": 1480, "tax_expense": 390, "depreciation_and_amortization": 480, "capex": 560, "operating_cash_flow": 1900, "cash_and_equivalents": 1250, "total_debt": 2500, "current_assets": 3400, "current_liabilities": 1980, "accounts_receivable": 980, "inventory": 760, "accounts_payable": 650, "diluted_shares_outstanding": 495, "basic_shares_outstanding": 485},
        {"fiscal_year": 2022, "revenue": 11650, "gross_profit": 6291, "operating_income": 2330, "net_income": 1685, "tax_expense": 445, "depreciation_and_amortization": 515, "capex": 620, "operating_cash_flow": 2150, "cash_and_equivalents": 1425, "total_debt": 2400, "current_assets": 3700, "current_liabilities": 2125, "accounts_receivable": 1060, "inventory": 830, "accounts_payable": 710, "diluted_shares_outstanding": 488, "basic_shares_outstanding": 478},
        {"fiscal_year": 2023, "revenue": 12450, "gross_profit": 6848, "operating_income": 2615, "net_income": 1905, "tax_expense": 505, "depreciation_and_amortization": 550, "capex": 690, "operating_cash_flow": 2425, "cash_and_equivalents": 1600, "total_debt": 2300, "current_assets": 4050, "current_liabilities": 2300, "accounts_receivable": 1150, "inventory": 910, "accounts_payable": 780, "diluted_shares_outstanding": 480, "basic_shares_outstanding": 470},
        {"fiscal_year": 2024, "revenue": 13400, "gross_profit": 7504, "operating_income": 2948, "net_income": 2160, "tax_expense": 575, "depreciation_and_amortization": 590, "capex": 750, "operating_cash_flow": 2750, "cash_and_equivalents": 1825, "total_debt": 2200, "current_assets": 4425, "current_liabilities": 2475, "accounts_receivable": 1250, "inventory": 985, "accounts_payable": 850, "diluted_shares_outstanding": 472, "basic_shares_outstanding": 462},
    ]
    df = pd.DataFrame(data).set_index("fiscal_year")
    df["operating_working_capital"] = df["accounts_receivable"] + df["inventory"] - df["accounts_payable"]
    df["free_cash_flow"] = df["operating_cash_flow"] - df["capex"]
    metadata = {"ticker": "DEMO", "company_name": "Demo Industrial Company", "cik": "0000000000"}
    warnings = ["Using built-in demo data; figures are generic and not investment advice."]
    return df, metadata, warnings


def ensure_standard_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure expected columns exist and calculate common derived items."""
    out = df.copy()
    for col in REQUIRED_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    if out["operating_working_capital"].isna().all():
        out["operating_working_capital"] = out["accounts_receivable"].fillna(0) + out["inventory"].fillna(0) - out["accounts_payable"].fillna(0)
    if out["free_cash_flow"].isna().all() and "operating_cash_flow" in out:
        out["free_cash_flow"] = out["operating_cash_flow"] - out["capex"]
    return out
