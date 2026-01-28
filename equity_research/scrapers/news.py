"""Financial news scraper using Yahoo Finance RSS feed."""

from __future__ import annotations

import logging
from xml.etree import ElementTree

from equity_research.models import NewsItem
from equity_research.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

YAHOO_RSS_URL = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

MAX_NEWS_ITEMS = 15


class NewsScraper(BaseScraper):
    """Fetches latest news headlines for a stock ticker from Yahoo Finance RSS."""

    def scrape(self) -> list[NewsItem]:
        """Return recent news items for the ticker."""
        url = YAHOO_RSS_URL.format(ticker=self.ticker)
        try:
            resp = self._get(url)
        except Exception as exc:
            logger.warning("Failed to fetch news RSS for %s: %s", self.ticker, exc)
            return []

        return self._parse_rss(resp.text)

    @staticmethod
    def _parse_rss(xml_text: str) -> list[NewsItem]:
        """Parse the RSS XML feed into NewsItem objects."""
        items: list[NewsItem] = []
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as exc:
            logger.warning("Failed to parse RSS XML: %s", exc)
            return items

        channel = root.find("channel")
        if channel is None:
            return items

        for item_el in channel.findall("item"):
            if len(items) >= MAX_NEWS_ITEMS:
                break
            title = item_el.findtext("title", "").strip()
            link = item_el.findtext("link", "").strip()
            pub_date = item_el.findtext("pubDate", "").strip()
            source = item_el.findtext("source", "").strip()

            if title:
                items.append(
                    NewsItem(
                        title=title,
                        link=link,
                        published=pub_date,
                        source=source,
                    )
                )

        return items
