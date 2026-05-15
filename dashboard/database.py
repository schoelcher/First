"""SQLite caching layer for scraped research data."""

import json
import sqlite3
import time
from pathlib import Path

from dashboard.config import CACHE_DB, CACHE_TTL_HOURS

_DB_PATH = Path(CACHE_DB)

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS research_cache (
    ticker     TEXT NOT NULL,
    section    TEXT NOT NULL,
    data       TEXT NOT NULL,
    scraped_at REAL NOT NULL,
    PRIMARY KEY (ticker, section)
)
"""


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(_DB_PATH))
    c.row_factory = sqlite3.Row
    c.execute(_CREATE_SQL)
    c.commit()
    return c


def get_cached(ticker: str, section: str) -> dict | None:
    con = _conn()
    try:
        row = con.execute(
            "SELECT data, scraped_at FROM research_cache WHERE ticker=? AND section=?",
            (ticker.upper(), section),
        ).fetchone()
        if row is None:
            return None
        if (time.time() - row["scraped_at"]) / 3600 > CACHE_TTL_HOURS:
            return None
        return json.loads(row["data"])
    finally:
        con.close()


def set_cached(ticker: str, section: str, data: dict) -> None:
    con = _conn()
    try:
        con.execute(
            "INSERT OR REPLACE INTO research_cache (ticker, section, data, scraped_at) "
            "VALUES (?,?,?,?)",
            (ticker.upper(), section, json.dumps(data, default=str), time.time()),
        )
        con.commit()
    finally:
        con.close()


def clear_cache(ticker: str | None = None) -> None:
    con = _conn()
    try:
        if ticker:
            con.execute("DELETE FROM research_cache WHERE ticker=?", (ticker.upper(),))
        else:
            con.execute("DELETE FROM research_cache")
        con.commit()
    finally:
        con.close()
