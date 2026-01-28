"""Abstract base class for all scrapers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

REQUEST_TIMEOUT = 15


class BaseScraper(ABC):
    """Base class providing shared HTTP utilities for all scrapers."""

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker.upper()
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get(self, url: str, **kwargs) -> requests.Response:
        """Perform a GET request with default timeout and error handling."""
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    def scrape(self):
        """Execute the scraping logic. Subclasses must implement this."""
        ...
