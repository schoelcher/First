"""SEC EDGAR company facts ingestion and normalization."""
from __future__ import annotations

import os
from collections import defaultdict
from typing import Any

import pandas as pd
import requests

from .ticker_mapper import DEFAULT_USER_AGENT, resolve_ticker
from ..model.normalized_financials import ensure_standard_columns

COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

TAG_MAPPINGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet", "SalesRevenueServicesNet"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "tax_expense": ["IncomeTaxExpenseBenefit"],
    "depreciation_and_amortization": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationDepletionAndAmortizationExpense", "Depreciation"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "CapitalExpenditures"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "cash_and_equivalents": ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "CashAndDueFromBanks"],
    "total_debt": ["DebtCurrent", "LongTermDebtCurrent", "LongTermDebtNoncurrent", "LongTermDebtAndFinanceLeaseObligationsCurrent", "LongTermDebtAndFinanceLeaseObligationsNoncurrent", "ShortTermBorrowings", "DebtAndFinanceLeaseObligations"],
    "current_assets": ["AssetsCurrent"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "accounts_receivable": ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"],
    "inventory": ["InventoryNet", "InventoryFinishedGoodsNetOfReserves"],
    "accounts_payable": ["AccountsPayableCurrent"],
    "diluted_shares_outstanding": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "basic_shares_outstanding": ["WeightedAverageNumberOfSharesOutstandingBasic", "EntityCommonStockSharesOutstanding"],
}

BALANCE_SHEET_ITEMS = {"cash_and_equivalents", "total_debt", "current_assets", "current_liabilities", "accounts_receivable", "inventory", "accounts_payable"}


def _headers() -> dict[str, str]:
    return {"User-Agent": os.getenv("SEC_USER_AGENT", DEFAULT_USER_AGENT)}


def fetch_company_facts(cik: str) -> dict[str, Any]:
    """Fetch SEC company facts JSON for a padded CIK."""
    response = requests.get(COMPANY_FACTS_URL.format(cik=cik), headers=_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


def _select_usd_units(fact: dict[str, Any], normalized_item: str) -> list[dict[str, Any]]:
    units = fact.get("units", {})
    if "shares" in normalized_item:
        return units.get("shares", [])
    return units.get("USD", []) or units.get("USD/shares", [])


def _annual_10k_facts(fact: dict[str, Any], normalized_item: str) -> list[dict[str, Any]]:
    candidates = []
    for unit_fact in _select_usd_units(fact, normalized_item):
        if unit_fact.get("form") not in {"10-K", "10-K/A"}:
            continue
        fiscal_year = unit_fact.get("fy")
        if not fiscal_year:
            continue
        if normalized_item not in BALANCE_SHEET_ITEMS and unit_fact.get("fp") not in {"FY", None}:
            continue
        candidates.append(unit_fact)
    return candidates


def normalize_company_facts(company_facts: dict[str, Any]) -> tuple[pd.DataFrame, list[str]]:
    """Normalize SEC company facts to one row per fiscal year."""
    warnings: list[str] = []
    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})
    year_rows: dict[int, dict[str, float]] = defaultdict(dict)
    used_tags: dict[str, str] = {}
    for normalized_item, tags in TAG_MAPPINGS.items():
        found = False
        selected_tags: list[str] = []
        for tag in tags:
            if tag not in us_gaap:
                continue
            facts = _annual_10k_facts(us_gaap[tag], normalized_item)
            if not facts:
                continue
            latest_by_year: dict[int, dict[str, Any]] = {}
            for fact in facts:
                year = int(fact["fy"])
                if year not in latest_by_year or str(fact.get("filed", "")) >= str(latest_by_year[year].get("filed", "")):
                    latest_by_year[year] = fact
            for year, fact in latest_by_year.items():
                value = fact.get("val")
                if value is None:
                    continue
                if normalized_item == "total_debt" and tag != "DebtAndFinanceLeaseObligations":
                    year_rows[year][normalized_item] = float(year_rows[year].get(normalized_item, 0.0) or 0.0) + float(value)
                else:
                    year_rows[year][normalized_item] = float(value)
            selected_tags.append(tag)
            found = True
            if normalized_item != "total_debt" or tag == "DebtAndFinanceLeaseObligations":
                break
        if found:
            used_tags[normalized_item] = "+".join(selected_tags)
        else:
            warnings.append(f"Missing SEC line item: {normalized_item}")
    if not year_rows:
        raise ValueError("No annual 10-K SEC financial facts found.")
    df = pd.DataFrame.from_dict(year_rows, orient="index").sort_index().tail(5)
    df.index.name = "fiscal_year"
    if "capex" in df:
        df["capex"] = df["capex"].abs()
    df = ensure_standard_columns(df)
    if df["free_cash_flow"].isna().all() and not df["operating_cash_flow"].isna().all():
        df["free_cash_flow"] = df["operating_cash_flow"] - df["capex"].fillna(0)
    if df["diluted_shares_outstanding"].isna().all():
        df["diluted_shares_outstanding"] = df["basic_shares_outstanding"]
        warnings.append("Using basic shares because diluted shares were unavailable.")
    warnings.append("SEC tags used: " + ", ".join(f"{k}={v}" for k, v in sorted(used_tags.items())))
    return df, warnings


def fetch_normalized_financials(ticker: str) -> tuple[pd.DataFrame, dict, list[str]]:
    """Resolve a ticker, fetch SEC facts, and return normalized financials."""
    metadata = resolve_ticker(ticker)
    facts = fetch_company_facts(metadata["cik"])
    df, warnings = normalize_company_facts(facts)
    return df, metadata, warnings
