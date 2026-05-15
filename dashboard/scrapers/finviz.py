"""Finviz scraper – snapshot metrics, analyst ratings, and news."""

import logging

from dashboard.scrapers.browser import browser_manager

logger = logging.getLogger(__name__)


async def scrape_finviz(ticker: str) -> dict:
    page = await browser_manager.new_page()
    result: dict = {"metrics": {}, "news": [], "ratings": []}
    try:
        await page.goto(
            f"https://finviz.com/quote.ashx?t={ticker.upper()}&p=d",
            wait_until="domcontentloaded",
            timeout=30000,
        )

        # Snapshot metric table
        try:
            await page.wait_for_selector("table.snapshot-table2", timeout=10000)
            for row in await page.query_selector_all("table.snapshot-table2 tr"):
                cells = await row.query_selector_all("td")
                i = 0
                while i < len(cells) - 1:
                    label = (await cells[i].inner_text()).strip()
                    value = (await cells[i + 1].inner_text()).strip()
                    if label:
                        result["metrics"][label] = value
                    i += 2
        except Exception as exc:
            logger.debug("Finviz metrics table: %s", exc)

        # News
        try:
            for row in (await page.query_selector_all("table.fullview-news-outer tr"))[:25]:
                date_el = await row.query_selector("td:first-child")
                link_el = await row.query_selector("a.tab-link-news")
                src_el = await row.query_selector("span")
                if link_el:
                    result["news"].append({
                        "title": (await link_el.inner_text()).strip(),
                        "url": await link_el.get_attribute("href") or "",
                        "date": (await date_el.inner_text()).strip() if date_el else "",
                        "source": (await src_el.inner_text()).strip("() ") if src_el else "",
                    })
        except Exception as exc:
            logger.debug("Finviz news: %s", exc)

        # Analyst ratings
        try:
            for row in (await page.query_selector_all("table.fullview-ratings-outer tr"))[:20]:
                cells = await row.query_selector_all("td")
                if len(cells) >= 5:
                    result["ratings"].append({
                        "date": (await cells[0].inner_text()).strip(),
                        "action": (await cells[1].inner_text()).strip(),
                        "firm": (await cells[2].inner_text()).strip(),
                        "rating": (await cells[3].inner_text()).strip(),
                        "price_target": (await cells[4].inner_text()).strip(),
                    })
        except Exception as exc:
            logger.debug("Finviz ratings: %s", exc)

    except Exception as exc:
        logger.error("Finviz scrape failed for %s: %s", ticker, exc)
        result["error"] = str(exc)
    finally:
        await page.context.close()
    return result
