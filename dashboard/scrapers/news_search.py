"""Google News scraper – quality financial article search via Playwright."""

import logging
from urllib.parse import urlparse

from dashboard.scrapers.browser import browser_manager

logger = logging.getLogger(__name__)

TIER1 = {"wsj.com", "bloomberg.com", "reuters.com", "ft.com", "barrons.com", "economist.com"}
TIER2 = {"seekingalpha.com", "fool.com", "marketwatch.com", "cnbc.com",
         "investopedia.com", "thestreet.com"}
TIER3 = {"benzinga.com", "zacks.com", "tipranks.com", "yahoo.com", "finance.yahoo.com"}


def _classify(href: str) -> tuple[str, str]:
    for d in TIER1:
        if d in href:
            return d.split(".")[0].upper(), "tier1"
    for d in TIER2:
        if d in href:
            return d.split(".")[0].capitalize(), "tier2"
    for d in TIER3:
        if d in href:
            return d.split(".")[0].capitalize(), "tier3"
    try:
        return urlparse(href).netloc.replace("www.", ""), "other"
    except Exception:
        return "Unknown", "other"


async def scrape_google_news(ticker: str, company_name: str = "") -> dict:
    page = await browser_manager.new_page()
    result: dict = {"articles": [], "deep_analysis": []}
    seen: set[str] = set()

    queries = [
        f"{ticker} stock analysis",
        f'"{ticker}" stock earnings outlook {company_name}'.strip(),
    ]
    try:
        for query in queries:
            try:
                await page.goto(
                    f"https://www.google.com/search?q={query}&tbm=nws&num=20",
                    wait_until="domcontentloaded",
                    timeout=20000,
                )
                await page.wait_for_timeout(2000)
                for a in await page.query_selector_all("a[href]"):
                    try:
                        href = await a.get_attribute("href") or ""
                        if not href.startswith("http") or "google.com" in href or href in seen:
                            continue
                        seen.add(href)
                        title_el = await a.query_selector("div[role='heading'], h3")
                        title = (await title_el.inner_text()).strip() if title_el else (await a.inner_text()).strip()[:200]
                        if not title or len(title) < 10:
                            continue
                        source_name, tier = _classify(href)
                        art = {"title": title, "url": href, "source": source_name, "tier": tier}
                        if tier in ("tier1", "tier2"):
                            result["deep_analysis"].append(art)
                        else:
                            result["articles"].append(art)
                    except Exception:
                        continue
            except Exception as exc:
                logger.debug("Google News query failed: %s", exc)

        result["deep_analysis"].sort(key=lambda x: 0 if x["tier"] == "tier1" else 1)
    except Exception as exc:
        logger.error("Google News scrape failed for %s: %s", ticker, exc)
        result["error"] = str(exc)
    finally:
        await page.context.close()
    return result
