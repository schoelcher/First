"""Aggregator that orchestrates all scrapers to build a complete research report."""

from __future__ import annotations

import logging
from typing import Optional

from equity_research.models import EquityResearchReport
from equity_research.scrapers.news import NewsScraper
from equity_research.scrapers.sec_edgar import SECEdgarScraper
from equity_research.scrapers.yahoo_finance import YahooFinanceScraper

logger = logging.getLogger(__name__)

ALL_SECTIONS = frozenset({"profile", "financials", "price", "analysts", "filings", "news"})


class EquityResearchAggregator:
    """Orchestrates multiple scrapers to build a unified equity research report."""

    def __init__(self, ticker: str, sections: Optional[set[str]] = None) -> None:
        self.ticker = ticker.upper()
        self.sections = sections or set(ALL_SECTIONS)

    def run(self) -> EquityResearchReport:
        """Execute all relevant scrapers and assemble the report."""
        report = EquityResearchReport(ticker=self.ticker)

        # Yahoo Finance covers profile, financials, price, and analysts
        yahoo_sections = {"profile", "financials", "price", "analysts"}
        if self.sections & yahoo_sections:
            self._scrape_yahoo(report)

        if "filings" in self.sections:
            self._scrape_sec(report)

        if "news" in self.sections:
            self._scrape_news(report)

        return report

    # ------------------------------------------------------------------
    # Private scraper runners
    # ------------------------------------------------------------------

    def _scrape_yahoo(self, report: EquityResearchReport) -> None:
        try:
            scraper = YahooFinanceScraper(self.ticker)
            profile, financials, price, analysts = scraper.scrape()

            if "profile" in self.sections:
                report.profile = profile
            if "financials" in self.sections:
                report.financials = financials
            if "price" in self.sections:
                report.price = price
            if "analysts" in self.sections:
                report.analysts = analysts

        except Exception as exc:
            msg = f"Yahoo Finance scraper failed: {exc}"
            logger.error(msg)
            report.errors.append(msg)

    def _scrape_sec(self, report: EquityResearchReport) -> None:
        try:
            scraper = SECEdgarScraper(self.ticker)
            report.filings = scraper.scrape()
        except Exception as exc:
            msg = f"SEC EDGAR scraper failed: {exc}"
            logger.error(msg)
            report.errors.append(msg)

    def _scrape_news(self, report: EquityResearchReport) -> None:
        try:
            scraper = NewsScraper(self.ticker)
            report.news = scraper.scrape()
        except Exception as exc:
            msg = f"News scraper failed: {exc}"
            logger.error(msg)
            report.errors.append(msg)
