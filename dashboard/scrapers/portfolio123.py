"""
Portfolio 123 API integration.

Auth:  POST /auth  {"apiId": P123_API_ID, "apiKey": P123_API_KEY}  → Bearer token
Data:  POST /data  with formula list, filtered to a single ticker via screen rule.

Docs:  https://api.portfolio123.com/docs/index.html
"""

from __future__ import annotations

import logging

import httpx

from dashboard.config import P123_API_ID, P123_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://api.portfolio123.com"

# Formulas to retrieve for each stock.
# Each entry: (p123_formula, display_label, format_hint)
# format_hint: "price" | "pct" | "ratio" | "int" | "raw"
_FORMULAS: list[tuple[str, str, str]] = [
    ("Close(0)",               "Price",                "price"),
    ("PE(0)",                  "P/E Ratio",            "ratio"),
    ("PB(0)",                  "Price / Book",         "ratio"),
    ("PS(0)",                  "Price / Sales",        "ratio"),
    ("EV2EBITDA(0)",           "EV / EBITDA",          "ratio"),
    ("Piotroski",              "Piotroski F-Score",    "int"),
    ("AltmanZ",                "Altman Z-Score",       "ratio"),
    ("ROE(0)",                 "Return on Equity",     "pct"),
    ("ROA(0)",                 "Return on Assets",     "pct"),
    ("GrossMargin(0)",         "Gross Margin",         "pct"),
    ("OperMargin(0)",          "Operating Margin",     "pct"),
    ("NetMargin(0)",           "Net Margin",           "pct"),
    ("SalesGr(0,TTM)",         "Revenue Growth (YoY)", "pct"),
    ("EPSGr(0,TTM)",           "EPS Growth (YoY)",     "pct"),
    ("Debt2Equity(0)",         "Debt / Equity",        "ratio"),
    ("CurrentRatio(0)",        "Current Ratio",        "ratio"),
    ("Beta(252)",              "Beta (252d)",          "ratio"),
    ("PctFromHi52",            "% from 52W High",      "pct"),
    ("FCalendarDaysToEarnings","Days to Earnings",     "int"),
    ("AvgDailyVolume(20)",     "Avg Vol (20d)",        "raw"),
]


async def fetch_portfolio123(ticker: str) -> dict:
    """Return P123 factor data for *ticker*, or an error dict."""
    if not P123_API_ID or not P123_API_KEY:
        return {"error": "not_configured", "metrics": []}

    ticker = ticker.upper()

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            # 1. Authenticate
            auth_resp = await client.post(
                f"{BASE_URL}/auth",
                json={"apiId": P123_API_ID, "apiKey": P123_API_KEY},
            )
            if auth_resp.status_code == 401:
                return {"error": "invalid_credentials", "metrics": []}
            auth_resp.raise_for_status()

            # Token is the raw response text (not JSON)
            token = auth_resp.text.strip().strip('"')
            headers = {"Authorization": f"Bearer {token}"}

            # 2. Request factor data for the specific ticker via a screen rule
            data_items = [
                {"formula": formula, "colName": col_name}
                for formula, col_name, _ in [(f, f.replace("(", "_").replace(")", "").replace(",", "_"), h)
                                              for f, _, h in _FORMULAS]
            ]

            body = {
                "screen": {
                    "type": "stock",
                    "universe": "All Fundamentals",
                    "rules": [{"formula": f'Ticker=="{ticker}"'}],
                },
                "asOfDt": "latest",
                "pitMethod": "Prelim",
                "precision": 4,
                "includeNa": True,
                "dataItems": [
                    {"formula": formula, "colName": f"col{i}"}
                    for i, (formula, _, _) in enumerate(_FORMULAS)
                ],
            }

            data_resp = await client.post(
                f"{BASE_URL}/data",
                headers=headers,
                json=body,
                timeout=httpx.Timeout(30.0),
            )
            data_resp.raise_for_status()
            raw = data_resp.json()

    except httpx.HTTPStatusError as exc:
        logger.error("P123 HTTP error %s: %s", exc.response.status_code, exc.response.text[:300])
        return {"error": f"http_{exc.response.status_code}", "metrics": []}
    except httpx.TimeoutException:
        return {"error": "timeout", "metrics": []}
    except Exception as exc:
        logger.error("P123 unexpected error: %s", exc)
        return {"error": str(exc), "metrics": []}

    # Parse response – rows keyed by P123 uid, each has a "row" list of values
    metrics: list[dict] = []
    try:
        # P123 /data returns {"columns": [...], "rows": [[val, val, ...], ...]}
        # or {"items": {"uid": {"ticker": ..., "row": [...]}}}
        # Handle both shapes defensively.
        rows = raw.get("rows") or []
        if not rows:
            items = raw.get("items", {})
            # Find the row for our ticker
            for uid_data in items.values():
                if str(uid_data.get("ticker", "")).upper() == ticker:
                    rows = [uid_data.get("row", [])]
                    break
            if not rows and items:
                # take first result (might be the only stock matching the screen)
                first = next(iter(items.values()))
                rows = [first.get("row", [])]

        if rows:
            row_values = rows[0]
            for i, (formula, label, fmt) in enumerate(_FORMULAS):
                raw_val = row_values[i] if i < len(row_values) else None
                metrics.append({
                    "label": label,
                    "formula": formula,
                    "value": raw_val,
                    "format": fmt,
                })
    except Exception as exc:
        logger.warning("P123 response parsing failed: %s", exc)
        return {"error": f"parse_error: {exc}", "raw_response": str(raw)[:500], "metrics": []}

    if not metrics:
        return {"error": "no_data", "metrics": [], "note": f"Ticker {ticker} may not be in the P123 universe."}

    return {"metrics": metrics, "ticker": ticker}
