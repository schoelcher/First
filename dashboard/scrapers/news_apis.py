"""
Multi-source news aggregator.

Fetches in parallel from:
  - Finnhub (company news API)
  - NewsAPI (keyword search)
  - Alpha Vantage News Sentiment (ticker-tagged, with sentiment scores)
  - Reuters RSS (filtered by ticker/company)
  - MarketWatch RSS (filtered by ticker/company)

All results are normalised to a common schema and deduplicated by URL.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from dashboard.config import ALPHA_VANTAGE_KEY, FINNHUB_API_KEY, NEWS_API_KEY

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(12.0)

# Normalised article schema
# {
#   "source": str,        display name
#   "source_id": str,     slug for badge CSS class
#   "headline": str,
#   "summary": str,
#   "url": str,
#   "published_at": str,  ISO-8601
#   "sentiment": str|None "positive" | "negative" | "neutral" | None
#   "sentiment_score": float|None  -1..1
#   "timed_out": bool
# }


def _article(
    source: str,
    source_id: str,
    headline: str,
    summary: str,
    url: str,
    published_at: str,
    sentiment: str | None = None,
    sentiment_score: float | None = None,
) -> dict:
    return {
        "source": source,
        "source_id": source_id,
        "headline": headline.strip(),
        "summary": (summary or "").strip(),
        "url": url.strip(),
        "published_at": published_at,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "timed_out": False,
    }


def _ts_from_unix(ts: int | float) -> str:
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def _map_sentiment(label: str, score: float | None) -> tuple[str | None, float | None]:
    """Map Alpha Vantage sentiment label → (positive|negative|neutral, score)."""
    label_lower = label.lower()
    if "bullish" in label_lower:
        return "positive", score
    if "bearish" in label_lower:
        return "negative", score
    if "neutral" in label_lower:
        return "neutral", score
    return None, score


# ---------------------------------------------------------------------------
# Individual source fetchers
# ---------------------------------------------------------------------------

async def _fetch_finnhub(ticker: str, client: httpx.AsyncClient) -> tuple[list[dict], str]:
    if not FINNHUB_API_KEY:
        return [], "no_key"
    try:
        today = datetime.now(tz=timezone.utc)
        from_dt = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        to_dt = today.strftime("%Y-%m-%d")
        resp = await client.get(
            "https://finnhub.io/api/v1/company-news",
            params={"symbol": ticker, "from": from_dt, "to": to_dt, "token": FINNHUB_API_KEY},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        articles = []
        for item in resp.json()[:25]:
            url = item.get("url", "")
            headline = item.get("headline", "")
            if not url or not headline:
                continue
            articles.append(_article(
                source="Finnhub",
                source_id="finnhub",
                headline=headline,
                summary=item.get("summary", ""),
                url=url,
                published_at=_ts_from_unix(item.get("datetime", 0)),
            ))
        return articles, "ok"
    except httpx.TimeoutException:
        logger.warning("Finnhub timed out")
        return [], "timeout"
    except Exception as exc:
        logger.warning("Finnhub error: %s", exc)
        return [], "error"


async def _fetch_newsapi(ticker: str, company_name: str, client: httpx.AsyncClient) -> tuple[list[dict], str]:
    if not NEWS_API_KEY:
        return [], "no_key"
    try:
        query = f'"{ticker}" OR "{company_name}"' if company_name else ticker
        resp = await client.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "apiKey": NEWS_API_KEY,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 25,
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = []
        for item in data.get("articles", []):
            url = item.get("url", "")
            title = item.get("title", "")
            if not url or not title or "[Removed]" in title:
                continue
            source_name = item.get("source", {}).get("name", "NewsAPI")
            articles.append(_article(
                source=source_name,
                source_id="newsapi",
                headline=title,
                summary=item.get("description", ""),
                url=url,
                published_at=item.get("publishedAt", ""),
            ))
        return articles, "ok"
    except httpx.TimeoutException:
        logger.warning("NewsAPI timed out")
        return [], "timeout"
    except Exception as exc:
        logger.warning("NewsAPI error: %s", exc)
        return [], "error"


async def _fetch_alphavantage(ticker: str, client: httpx.AsyncClient) -> tuple[list[dict], str]:
    if not ALPHA_VANTAGE_KEY:
        return [], "no_key"
    try:
        resp = await client.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "NEWS_SENTIMENT",
                "tickers": ticker,
                "apikey": ALPHA_VANTAGE_KEY,
                "limit": 25,
                "sort": "LATEST",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        # Rate-limit or error messages come back as plain dicts
        if "Information" in data or "Note" in data:
            logger.warning("Alpha Vantage API limit: %s", data.get("Information") or data.get("Note"))
            return [], "rate_limited"

        articles = []
        for item in data.get("feed", []):
            url = item.get("url", "")
            title = item.get("title", "")
            if not url or not title:
                continue

            raw_label = item.get("overall_sentiment_label", "")
            raw_score_str = item.get("overall_sentiment_score", None)
            try:
                raw_score: float | None = float(raw_score_str) if raw_score_str is not None else None
            except (ValueError, TypeError):
                raw_score = None

            # Prefer ticker-specific sentiment when available
            for ts in item.get("ticker_sentiment", []):
                if ts.get("ticker", "").upper() == ticker.upper():
                    raw_label = ts.get("ticker_sentiment_label", raw_label)
                    try:
                        raw_score = float(ts.get("ticker_sentiment_score", raw_score))
                    except (ValueError, TypeError):
                        pass
                    break

            sentiment, score = _map_sentiment(raw_label, raw_score)

            # AV timestamp format: "20240115T103000"
            raw_ts = item.get("time_published", "")
            try:
                pub = datetime.strptime(raw_ts, "%Y%m%dT%H%M%S").replace(
                    tzinfo=timezone.utc
                ).isoformat()
            except Exception:
                pub = ""

            articles.append(_article(
                source=item.get("source", "Alpha Vantage"),
                source_id="alphavantage",
                headline=title,
                summary=item.get("summary", ""),
                url=url,
                published_at=pub,
                sentiment=sentiment,
                sentiment_score=score,
            ))
        return articles, "ok"
    except httpx.TimeoutException:
        logger.warning("Alpha Vantage timed out")
        return [], "timeout"
    except Exception as exc:
        logger.warning("Alpha Vantage error: %s", exc)
        return [], "error"


async def _fetch_rss(
    feed_url: str,
    source_name: str,
    source_id: str,
    ticker: str,
    company_name: str,
    client: httpx.AsyncClient,
) -> tuple[list[dict], str]:
    """Fetch an RSS feed and filter items that mention the ticker or company."""
    try:
        resp = await client.get(feed_url, timeout=_TIMEOUT,
                                follow_redirects=True,
                                headers={"Accept": "application/rss+xml, application/xml, text/xml"})
        resp.raise_for_status()
        root = ElementTree.fromstring(resp.content)
    except httpx.TimeoutException:
        return [], "timeout"
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", feed_url, exc)
        return [], "error"

    # Words to match against headline/description
    keywords = {ticker.upper()}
    if company_name:
        # First meaningful word of company name, e.g. "Apple" from "Apple Inc."
        first_word = re.split(r"\s+", company_name.strip())[0]
        if len(first_word) > 3:
            keywords.add(first_word.upper())

    articles = []
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else root.findall(".//item")
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()

        combined = (title + " " + description).upper()
        if not any(kw in combined for kw in keywords):
            continue

        pub_dt = ""
        try:
            pub_dt = parsedate_to_datetime(pub_date_raw).isoformat()
        except Exception:
            pass

        if title and link:
            articles.append(_article(
                source=source_name,
                source_id=source_id,
                headline=title,
                summary=re.sub(r"<[^>]+>", "", description)[:300],
                url=link,
                published_at=pub_dt,
            ))

    return articles, "ok"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def fetch_all_news(ticker: str, company_name: str = "") -> dict:
    """
    Run all news sources in parallel and return a unified, deduplicated feed.
    """
    ticker = ticker.upper()

    async with httpx.AsyncClient(
        headers={"User-Agent": "EquityScope/1.0 (research dashboard)"},
        follow_redirects=True,
    ) as client:
        results = await asyncio.gather(
            _fetch_finnhub(ticker, client),
            _fetch_newsapi(ticker, company_name, client),
            _fetch_alphavantage(ticker, client),
            _fetch_rss(
                "https://feeds.reuters.com/reuters/businessNews",
                "Reuters", "reuters", ticker, company_name, client,
            ),
            _fetch_rss(
                "https://feeds.marketwatch.com/marketwatch/topstories",
                "MarketWatch", "marketwatch", ticker, company_name, client,
            ),
            return_exceptions=True,
        )

    source_names = ["Finnhub", "NewsAPI", "Alpha Vantage", "Reuters RSS", "MarketWatch RSS"]
    source_ids   = ["finnhub", "newsapi",  "alphavantage",  "reuters",     "marketwatch"]

    all_articles: list[dict] = []
    source_statuses: dict[str, str] = {}

    for i, result in enumerate(results):
        name = source_names[i]
        sid  = source_ids[i]
        if isinstance(result, Exception):
            logger.error("Source %s raised: %s", name, result)
            source_statuses[name] = "error"
            continue
        articles, status = result
        source_statuses[name] = status
        if status == "timeout":
            all_articles.append({
                **_article(name, sid, f"[{name} timed out]", "", "", ""),
                "timed_out": True,
            })
        else:
            all_articles.extend(articles)

    # Deduplicate by URL (case-insensitive, strip trailing slash)
    seen_urls: set[str] = set()
    unique: list[dict] = []
    for art in all_articles:
        key = art["url"].rstrip("/").lower()
        if key and key not in seen_urls:
            seen_urls.add(key)
            unique.append(art)

    # Sort by published_at descending; articles without a date go to the end
    def _sort_key(a: dict) -> str:
        return a["published_at"] or "0000"

    unique.sort(key=_sort_key, reverse=True)

    return {
        "articles": unique,
        "source_statuses": source_statuses,
    }
