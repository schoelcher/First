"""FastAPI application – serves the dashboard and streams research data via SSE."""

import json
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dashboard.database import clear_cache
from dashboard.scrapers.aggregator import research_ticker
from dashboard.scrapers.browser import browser_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent

app = FastAPI(title="EquityScope Research Dashboard", version="2.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
async def _startup():
    try:
        await browser_manager.start()
    except Exception as exc:
        logger.warning("Browser will start lazily on first request: %s", exc)


@app.on_event("shutdown")
async def _shutdown():
    await browser_manager.stop()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/research/{ticker}")
async def stream_research(ticker: str, nocache: bool = False):
    """Server-Sent Events stream – emits research sections as they arrive."""
    async def _gen():
        async for event in research_ticker(ticker, use_cache=not nocache):
            yield f"data: {json.dumps(event, default=str)}\n\n"
        yield 'data: {"section":"done","status":"complete"}\n\n'

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive",
                 "X-Accel-Buffering": "no"},
    )


@app.post("/api/cache/clear/{ticker}")
async def clear_ticker_cache(ticker: str):
    clear_cache(ticker)
    return {"status": "ok", "message": f"Cache cleared for {ticker.upper()}"}


@app.post("/api/cache/clear")
async def clear_all_cache():
    clear_cache()
    return {"status": "ok", "message": "All cache cleared"}
