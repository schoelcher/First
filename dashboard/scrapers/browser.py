"""Playwright browser manager – shared Chromium instance."""

import logging

from playwright.async_api import Browser, Page, async_playwright

from dashboard.config import HEADLESS

logger = logging.getLogger(__name__)

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class BrowserManager:
    def __init__(self) -> None:
        self._pw = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        if self._browser:
            return
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=HEADLESS)
        logger.info("Playwright browser started (headless=%s)", HEADLESS)

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._pw:
            await self._pw.stop()
            self._pw = None

    async def new_page(self) -> Page:
        if not self._browser:
            await self.start()
        ctx = await self._browser.new_context(
            user_agent=_UA,
            viewport={"width": 1920, "height": 1080},
        )
        return await ctx.new_page()


browser_manager = BrowserManager()
