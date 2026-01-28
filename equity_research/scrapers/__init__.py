"""Web scraping modules for equity research data collection."""

from equity_research.scrapers.yahoo_finance import YahooFinanceScraper
from equity_research.scrapers.sec_edgar import SECEdgarScraper
from equity_research.scrapers.news import NewsScraper

__all__ = ["YahooFinanceScraper", "SECEdgarScraper", "NewsScraper"]
