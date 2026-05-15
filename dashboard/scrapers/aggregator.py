"""Orchestrates all scrapers and yields SSE events as each section completes."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncGenerator

from equity_research.aggregator import EquityResearchAggregator

from dashboard.database import get_cached, set_cached
from dashboard.scrapers.browser import browser_manager
from dashboard.scrapers.finviz import scrape_finviz
from dashboard.scrapers.news_apis import fetch_all_news
from dashboard.scrapers.news_search import scrape_google_news
from dashboard.scrapers.openinsider import scrape_openinsider
from dashboard.scrapers.portfolio123 import fetch_portfolio123
from dashboard.scrapers.yahoo_analysis import scrape_yahoo_analysis

logger = logging.getLogger(__name__)


def _status(msg: str) -> dict:
    return {"section": "status", "data": {"message": msg}, "status": "progress"}


async def _tagged(section: str, coro):
    return section, await coro


def _run_base(ticker: str) -> dict:
    return EquityResearchAggregator(ticker).run().to_dict()


async def research_ticker(
    ticker: str, *, use_cache: bool = True
) -> AsyncGenerator[dict, None]:
    """
    Run every scraper for *ticker*, yielding SSE-ready dicts as each finishes.

    Shape: {"section": str, "data": dict, "status": "done"|"error"|"progress"}
    """
    ticker = ticker.upper().strip()
    yield _status(f"Starting research for {ticker}…")

    # ------------------------------------------------------------------
    # Phase 1 – yfinance / SEC / RSS  (synchronous, run in executor)
    # ------------------------------------------------------------------
    cached_base = get_cached(ticker, "base") if use_cache else None
    company_name = ""

    if cached_base:
        company_name = cached_base.get("profile", {}).get("name", "")
        yield {"section": "base", "data": cached_base, "status": "done"}
    else:
        yield _status("Fetching core financial data from Yahoo Finance…")
        try:
            loop = asyncio.get_event_loop()
            base_data = await loop.run_in_executor(None, _run_base, ticker)
            company_name = base_data.get("profile", {}).get("name", "")
            set_cached(ticker, "base", base_data)
            yield {"section": "base", "data": base_data, "status": "done"}
        except Exception as exc:
            logger.error("Base scraper failed: %s", exc)
            yield {"section": "base", "data": {"error": str(exc)}, "status": "error"}

    # ------------------------------------------------------------------
    # Phase 2 – Playwright + API scrapers (concurrent)
    # ------------------------------------------------------------------
    yield _status("Launching browser and API scrapers…")
    await browser_manager.start()

    scraper_defs: list[tuple[str, str, object, tuple]] = [
        ("finviz",         "Scraping Finviz…",                         scrape_finviz,        (ticker,)),
        ("yahoo_analysis", "Scraping Yahoo Finance analysis…",          scrape_yahoo_analysis, (ticker,)),
        ("insider",        "Scraping OpenInsider…",                     scrape_openinsider,   (ticker,)),
        ("news_deep",      "Searching Google News for articles…",       scrape_google_news,   (ticker, company_name)),
        ("news_apis",      "Fetching multi-source news feed…",          fetch_all_news,       (ticker, company_name)),
        ("portfolio123",   "Querying Portfolio 123…",                   fetch_portfolio123,   (ticker,)),
    ]

    tasks: list[asyncio.Task] = []
    for section, msg, func, args in scraper_defs:
        cached = get_cached(ticker, section) if use_cache else None
        if cached:
            yield {"section": section, "data": cached, "status": "done"}
        else:
            yield _status(msg)
            tasks.append(asyncio.create_task(_tagged(section, func(*args))))

    for coro in asyncio.as_completed(tasks):
        try:
            section, data = await coro
            set_cached(ticker, section, data)
            yield {"section": section, "data": data, "status": "done"}
        except Exception as exc:
            logger.error("Scraper task failed: %s", exc)
            yield {"section": "error", "data": {"error": str(exc)}, "status": "error"}

    yield {"section": "status", "data": {"message": "Research complete!"}, "status": "complete"}
