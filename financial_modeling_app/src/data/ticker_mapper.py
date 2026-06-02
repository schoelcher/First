"""SEC ticker-to-CIK mapping."""
from __future__ import annotations

import functools
import os

import requests

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
DEFAULT_USER_AGENT = "local-financial-modeling-app/0.1 contact@example.com"


def _headers() -> dict[str, str]:
    return {"User-Agent": os.getenv("SEC_USER_AGENT", DEFAULT_USER_AGENT)}


@functools.lru_cache(maxsize=1)
def fetch_ticker_mapping() -> dict[str, dict[str, str]]:
    """Fetch and cache SEC's public ticker mapping."""
    response = requests.get(SEC_TICKERS_URL, headers=_headers(), timeout=20)
    response.raise_for_status()
    raw = response.json()
    mapping: dict[str, dict[str, str]] = {}
    for entry in raw.values():
        ticker = str(entry["ticker"]).upper()
        mapping[ticker] = {
            "ticker": ticker,
            "cik": str(entry["cik_str"]).zfill(10),
            "company_name": entry["title"],
        }
    return mapping


def resolve_ticker(ticker: str) -> dict[str, str]:
    """Resolve a ticker to padded CIK and company name."""
    normalized = ticker.strip().upper()
    if not normalized:
        raise ValueError("Ticker is required.")
    mapping = fetch_ticker_mapping()
    if normalized not in mapping:
        raise KeyError(f"Ticker {normalized} not found in SEC mapping.")
    return mapping[normalized]
