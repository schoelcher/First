"""Tests for scraper modules."""

from unittest.mock import MagicMock, patch

from equity_research.models import NewsItem
from equity_research.scrapers.news import NewsScraper
from equity_research.scrapers.yahoo_finance import YahooFinanceScraper


class TestYahooFinanceScraper:
    """Tests for the Yahoo Finance scraper."""

    @patch("equity_research.scrapers.yahoo_finance.yf.Ticker")
    def test_scrape_returns_four_objects(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "longName": "Apple Inc.",
            "ticker": "AAPL",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "marketCap": 3_000_000_000_000,
            "trailingPE": 30.0,
            "currentPrice": 195.0,
            "fiftyTwoWeekHigh": 200.0,
            "fiftyTwoWeekLow": 140.0,
            "targetMeanPrice": 210.0,
            "recommendationKey": "buy",
            "city": "Cupertino",
            "state": "CA",
            "country": "United States",
        }
        mock_ticker_cls.return_value = mock_ticker

        scraper = YahooFinanceScraper("AAPL")
        profile, financials, price, analysts = scraper.scrape()

        assert profile.name == "Apple Inc."
        assert profile.sector == "Technology"
        assert profile.headquarters == "Cupertino, CA, United States"
        assert financials.market_cap == 3_000_000_000_000
        assert financials.trailing_pe == 30.0
        assert price.current_price == 195.0
        assert price.fifty_two_week_high == 200.0
        assert analysts.target_mean == 210.0
        assert analysts.recommendation == "buy"

    @patch("equity_research.scrapers.yahoo_finance.yf.Ticker")
    def test_scrape_handles_missing_fields(self, mock_ticker_cls):
        mock_ticker = MagicMock()
        mock_ticker.info = {}
        mock_ticker_cls.return_value = mock_ticker

        scraper = YahooFinanceScraper("UNKNOWN")
        profile, financials, price, analysts = scraper.scrape()

        assert profile.name == ""
        assert financials.market_cap is None
        assert price.current_price is None
        assert analysts.recommendation == ""


class TestNewsScraper:
    """Tests for the news RSS scraper."""

    SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Yahoo Finance News</title>
        <item>
          <title>Apple reports record earnings</title>
          <link>https://news.example.com/1</link>
          <pubDate>Mon, 01 Jan 2024 12:00:00 +0000</pubDate>
          <source>Reuters</source>
        </item>
        <item>
          <title>Tech sector rally continues</title>
          <link>https://news.example.com/2</link>
          <pubDate>Mon, 01 Jan 2024 10:00:00 +0000</pubDate>
          <source>Bloomberg</source>
        </item>
      </channel>
    </rss>"""

    def test_parse_rss(self):
        items = NewsScraper._parse_rss(self.SAMPLE_RSS)
        assert len(items) == 2
        assert items[0].title == "Apple reports record earnings"
        assert items[0].source == "Reuters"
        assert items[1].title == "Tech sector rally continues"
        assert items[1].link == "https://news.example.com/2"

    def test_parse_rss_empty(self):
        xml = """<?xml version="1.0"?><rss><channel></channel></rss>"""
        items = NewsScraper._parse_rss(xml)
        assert items == []

    def test_parse_rss_invalid_xml(self):
        items = NewsScraper._parse_rss("not xml at all")
        assert items == []
