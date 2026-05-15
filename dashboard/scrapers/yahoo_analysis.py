"""Yahoo Finance analysis page scraper."""

import logging

from dashboard.scrapers.browser import browser_manager

logger = logging.getLogger(__name__)


async def scrape_yahoo_analysis(ticker: str) -> dict:
    page = await browser_manager.new_page()
    result: dict = {"tables": [], "upgrades_downgrades": []}
    try:
        await page.goto(
            f"https://finance.yahoo.com/quote/{ticker.upper()}/analysis/",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        try:
            btn = await page.wait_for_selector(
                "button[name='agree'], button[data-testid='consent-accept']",
                timeout=3000,
            )
            if btn:
                await btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        try:
            await page.wait_for_selector("table", timeout=12000)
        except Exception:
            pass

        for section in await page.query_selector_all("section"):
            h_el = await section.query_selector("h2, h3")
            heading = (await h_el.inner_text()).strip() if h_el else ""
            table = await section.query_selector("table")
            if not table:
                continue
            headers: list[str] = []
            hrow = await table.query_selector("thead tr")
            if hrow:
                headers = [(await th.inner_text()).strip()
                           for th in await hrow.query_selector_all("th")]
            rows_data: list[list[str]] = []
            for tr in await table.query_selector_all("tbody tr"):
                rows_data.append([(await c.inner_text()).strip()
                                  for c in await tr.query_selector_all("td")])
            if headers or rows_data:
                result["tables"].append(
                    {"heading": heading, "headers": headers, "rows": rows_data}
                )

        # Upgrades/downgrades page
        try:
            await page.goto(
                f"https://finance.yahoo.com/quote/{ticker.upper()}/upgrades-downgrades/",
                wait_until="domcontentloaded",
                timeout=20000,
            )
            await page.wait_for_selector("table", timeout=8000)
            ud_table = await page.query_selector("table")
            if ud_table:
                for tr in (await ud_table.query_selector_all("tbody tr"))[:25]:
                    texts = [(await c.inner_text()).strip()
                             for c in await tr.query_selector_all("td")]
                    if len(texts) >= 4:
                        result["upgrades_downgrades"].append({
                            "date": texts[0],
                            "firm": texts[1],
                            "action": texts[2],
                            "details": texts[3] if len(texts) > 3 else "",
                        })
        except Exception:
            logger.debug("Yahoo upgrades/downgrades unavailable for %s", ticker)

    except Exception as exc:
        logger.error("Yahoo Analysis scrape failed for %s: %s", ticker, exc)
        result["error"] = str(exc)
    finally:
        await page.context.close()
    return result
