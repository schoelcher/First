"""Yahoo Finance scraper using the yfinance library."""

from __future__ import annotations

import logging

import yfinance as yf

from equity_research.models import (
    AnalystData,
    CompanyProfile,
    FinancialData,
    PriceData,
)
from equity_research.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class YahooFinanceScraper(BaseScraper):
    """Fetches company data from Yahoo Finance via yfinance."""

    def __init__(self, ticker: str) -> None:
        super().__init__(ticker)
        self._yf_ticker = yf.Ticker(self.ticker)
        self._info: dict = {}

    def scrape(self) -> tuple[CompanyProfile, FinancialData, PriceData, AnalystData]:
        """Fetch all available data and return structured objects."""
        self._info = self._yf_ticker.info or {}
        return (
            self._build_profile(),
            self._build_financials(),
            self._build_price(),
            self._build_analysts(),
        )

    # ------------------------------------------------------------------
    # Private builders
    # ------------------------------------------------------------------

    def _get(self, key: str, default=None):
        """Retrieve a value from the cached info dict."""
        return self._info.get(key, default)

    def _build_profile(self) -> CompanyProfile:
        city = self._get("city", "")
        state = self._get("state", "")
        country = self._get("country", "")
        hq_parts = [p for p in (city, state, country) if p]

        return CompanyProfile(
            ticker=self.ticker,
            name=self._get("longName", self._get("shortName", "")),
            sector=self._get("sector", ""),
            industry=self._get("industry", ""),
            description=self._get("longBusinessSummary", ""),
            website=self._get("website", ""),
            headquarters=", ".join(hq_parts),
            employees=self._get("fullTimeEmployees"),
            exchange=self._get("exchange", ""),
            currency=self._get("currency", ""),
        )

    def _build_financials(self) -> FinancialData:
        return FinancialData(
            market_cap=self._get("marketCap"),
            enterprise_value=self._get("enterpriseValue"),
            trailing_pe=self._get("trailingPE"),
            forward_pe=self._get("forwardPE"),
            peg_ratio=self._get("pegRatio"),
            price_to_book=self._get("priceToBook"),
            price_to_sales=self._get("priceToSalesTrailing12Months"),
            earnings_per_share=self._get("trailingEps"),
            revenue=self._get("totalRevenue"),
            revenue_growth=self._get("revenueGrowth"),
            gross_margins=self._get("grossMargins"),
            operating_margins=self._get("operatingMargins"),
            profit_margins=self._get("profitMargins"),
            return_on_equity=self._get("returnOnEquity"),
            return_on_assets=self._get("returnOnAssets"),
            debt_to_equity=self._get("debtToEquity"),
            current_ratio=self._get("currentRatio"),
            free_cash_flow=self._get("freeCashflow"),
            dividend_yield=self._get("dividendYield"),
            dividend_rate=self._get("dividendRate"),
            payout_ratio=self._get("payoutRatio"),
            book_value=self._get("bookValue"),
            total_cash=self._get("totalCash"),
            total_debt=self._get("totalDebt"),
        )

    def _build_price(self) -> PriceData:
        return PriceData(
            current_price=self._get(
                "currentPrice", self._get("regularMarketPrice")
            ),
            previous_close=self._get("previousClose", self._get("regularMarketPreviousClose")),
            open_price=self._get("open", self._get("regularMarketOpen")),
            day_low=self._get("dayLow", self._get("regularMarketDayLow")),
            day_high=self._get("dayHigh", self._get("regularMarketDayHigh")),
            fifty_two_week_low=self._get("fiftyTwoWeekLow"),
            fifty_two_week_high=self._get("fiftyTwoWeekHigh"),
            fifty_day_average=self._get("fiftyDayAverage"),
            two_hundred_day_average=self._get("twoHundredDayAverage"),
            volume=self._get("volume", self._get("regularMarketVolume")),
            average_volume=self._get("averageVolume"),
            beta=self._get("beta"),
        )

    def _build_analysts(self) -> AnalystData:
        return AnalystData(
            target_high=self._get("targetHighPrice"),
            target_low=self._get("targetLowPrice"),
            target_mean=self._get("targetMeanPrice"),
            target_median=self._get("targetMedianPrice"),
            recommendation=self._get("recommendationKey", ""),
            number_of_analysts=self._get("numberOfAnalystOpinions"),
        )
