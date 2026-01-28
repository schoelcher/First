"""Tests for the aggregator module."""

from unittest.mock import MagicMock, patch

from equity_research.aggregator import EquityResearchAggregator
from equity_research.models import (
    AnalystData,
    CompanyProfile,
    EquityResearchReport,
    FinancialData,
    PriceData,
)


class TestEquityResearchAggregator:
    @patch("equity_research.aggregator.NewsScraper")
    @patch("equity_research.aggregator.SECEdgarScraper")
    @patch("equity_research.aggregator.YahooFinanceScraper")
    def test_run_all_sections(self, mock_yf_cls, mock_sec_cls, mock_news_cls):
        # Setup mocks
        mock_yf = MagicMock()
        mock_yf.scrape.return_value = (
            CompanyProfile(ticker="AAPL", name="Apple Inc."),
            FinancialData(market_cap=3_000_000_000_000),
            PriceData(current_price=195.0),
            AnalystData(recommendation="buy"),
        )
        mock_yf_cls.return_value = mock_yf

        mock_sec = MagicMock()
        mock_sec.scrape.return_value = []
        mock_sec_cls.return_value = mock_sec

        mock_news = MagicMock()
        mock_news.scrape.return_value = []
        mock_news_cls.return_value = mock_news

        aggregator = EquityResearchAggregator("AAPL")
        report = aggregator.run()

        assert report.ticker == "AAPL"
        assert report.profile.name == "Apple Inc."
        assert report.financials.market_cap == 3_000_000_000_000
        assert report.price.current_price == 195.0
        assert report.analysts.recommendation == "buy"
        assert report.errors == []

    @patch("equity_research.aggregator.YahooFinanceScraper")
    def test_run_selected_sections(self, mock_yf_cls):
        mock_yf = MagicMock()
        mock_yf.scrape.return_value = (
            CompanyProfile(ticker="MSFT", name="Microsoft"),
            FinancialData(),
            PriceData(),
            AnalystData(),
        )
        mock_yf_cls.return_value = mock_yf

        aggregator = EquityResearchAggregator("MSFT", sections={"profile"})
        report = aggregator.run()

        assert report.profile.name == "Microsoft"
        # Financials should remain default since not in sections
        assert report.financials.market_cap is None

    @patch("equity_research.aggregator.YahooFinanceScraper")
    def test_run_handles_scraper_failure(self, mock_yf_cls):
        mock_yf = MagicMock()
        mock_yf.scrape.side_effect = RuntimeError("Connection failed")
        mock_yf_cls.return_value = mock_yf

        aggregator = EquityResearchAggregator("FAIL", sections={"profile"})
        report = aggregator.run()

        assert len(report.errors) == 1
        assert "Yahoo Finance scraper failed" in report.errors[0]


class TestAggregatorTickerNormalization:
    def test_ticker_uppercased(self):
        agg = EquityResearchAggregator("aapl")
        assert agg.ticker == "AAPL"
