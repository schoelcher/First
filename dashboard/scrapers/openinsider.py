"""OpenInsider scraper – insider buy/sell transactions."""

import logging

from dashboard.scrapers.browser import browser_manager

logger = logging.getLogger(__name__)

_URL = (
    "http://openinsider.com/screener?s={ticker}&o=&pl=&ph=&st=0&lt=0&lk="
    "&isceo=1&iscfo=1&is10=1&isvp=1&isd=1&ido=1"
)


def _int(text: str) -> int:
    try:
        return int(text.replace(",", "").replace("$", "").replace("+", "").replace("-", "").strip())
    except (ValueError, TypeError):
        return 0


async def scrape_openinsider(ticker: str) -> dict:
    page = await browser_manager.new_page()
    result: dict = {"transactions": [], "summary": {}}
    try:
        await page.goto(_URL.format(ticker=ticker.upper()),
                        wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("table.tinytable", timeout=10000)

        buys, sells, buy_val, sell_val = 0, 0, 0, 0
        for row in (await page.query_selector_all("table.tinytable tbody tr"))[:30]:
            cells = await row.query_selector_all("td")
            if len(cells) < 12:
                continue
            t = [(await c.inner_text()).strip() for c in cells]
            trade_type = t[6] if len(t) > 6 else ""
            value_str = t[11] if len(t) > 11 else ""
            result["transactions"].append({
                "filing_date": t[1] if len(t) > 1 else "",
                "trade_date": t[2] if len(t) > 2 else "",
                "insider_name": t[4] if len(t) > 4 else "",
                "title": t[5] if len(t) > 5 else "",
                "trade_type": trade_type,
                "price": t[7] if len(t) > 7 else "",
                "qty": t[8] if len(t) > 8 else "",
                "owned": t[9] if len(t) > 9 else "",
                "delta_own": t[10] if len(t) > 10 else "",
                "value": value_str,
            })
            dollar = _int(value_str)
            if "Purchase" in trade_type or "Buy" in trade_type:
                buys += 1; buy_val += dollar
            elif "Sale" in trade_type or "Sell" in trade_type:
                sells += 1; sell_val += dollar

        result["summary"] = {
            "total_buys": buys,
            "total_sells": sells,
            "total_buy_value": buy_val,
            "total_sell_value": sell_val,
            "net_sentiment": "Bullish" if buys > sells else "Bearish" if sells > buys else "Neutral",
        }
    except Exception as exc:
        logger.error("OpenInsider failed for %s: %s", ticker, exc)
        result["error"] = str(exc)
    finally:
        await page.context.close()
    return result
