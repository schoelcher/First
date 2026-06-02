"""Optional yfinance market-data fetcher with graceful fallback."""
from __future__ import annotations


def fetch_market_data(ticker: str) -> tuple[dict, list[str]]:
    """Fetch current market data; never raise on failure."""
    warnings: list[str] = []
    result = {
        "current_share_price": None,
        "market_cap": None,
        "beta": None,
        "shares_outstanding": None,
        "total_debt": None,
        "cash": None,
    }
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker)
        info = stock.info or {}
        fast_info = getattr(stock, "fast_info", {}) or {}
        result.update(
            {
                "current_share_price": info.get("currentPrice") or info.get("regularMarketPrice") or fast_info.get("last_price"),
                "market_cap": info.get("marketCap") or fast_info.get("market_cap"),
                "beta": info.get("beta"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "total_debt": info.get("totalDebt"),
                "cash": info.get("totalCash"),
            }
        )
    except Exception as exc:  # noqa: BLE001 - this fallback is intentional for local resilience.
        warnings.append(f"Market data unavailable from yfinance: {exc}")
    return result, warnings
