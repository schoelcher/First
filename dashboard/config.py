"""Configuration – reads from environment / .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (silent if it doesn't exist)
load_dotenv(Path(__file__).parent.parent / ".env")

# Server
HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
PORT = int(os.getenv("DASHBOARD_PORT", "8000"))

# Cache
CACHE_DB = os.getenv("DASHBOARD_CACHE_DB", "research_cache.db")
CACHE_TTL_HOURS = int(os.getenv("DASHBOARD_CACHE_TTL_HOURS", "4"))

# Playwright
HEADLESS = os.getenv("DASHBOARD_HEADLESS", "true").lower() == "true"

# News API keys
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")

# Portfolio 123
P123_API_ID = os.getenv("P123_API_ID", "")
P123_API_KEY = os.getenv("P123_API_KEY", "")
