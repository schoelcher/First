"""SEC EDGAR scraper for regulatory filings."""

from __future__ import annotations

import logging
from typing import Optional

from equity_research.models import SECFiling
from equity_research.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

EDGAR_COMPANY_SEARCH_URL = (
    "https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom"
    "&startdt={start}&enddt={end}&forms={forms}"
)

EDGAR_FULL_TEXT_SEARCH_URL = (
    "https://efts.sec.gov/LATEST/search-index"
    "?q=%22{cik}%22&forms={forms}&dateRange=custom&startdt={start}&enddt={end}"
)

EDGAR_CIK_LOOKUP_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK={ticker}&type=&dateb=&owner=include&count=1&search_text=&action=getcompany"

EDGAR_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

EDGAR_FILING_BASE_URL = "https://www.sec.gov/Archives/edgar/data"

FILING_TYPES = ["10-K", "10-Q", "8-K"]
MAX_FILINGS = 10


class SECEdgarScraper(BaseScraper):
    """Fetches recent SEC filings from EDGAR for a given ticker."""

    def __init__(self, ticker: str) -> None:
        super().__init__(ticker)
        # EDGAR requires a descriptive User-Agent with contact info per their policy
        self.session.headers.update(
            {
                "User-Agent": "EquityResearchTool/0.1 (equity-research-scraper)",
                "Accept": "application/json",
            }
        )

    def scrape(self) -> list[SECFiling]:
        """Return recent SEC filings for the ticker."""
        cik = self._resolve_cik()
        if cik is None:
            logger.warning("Could not resolve CIK for %s", self.ticker)
            return []
        return self._fetch_filings(cik)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_cik(self) -> Optional[str]:
        """Look up the SEC CIK number for the ticker."""
        url = "https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "company": "",
            "CIK": self.ticker,
            "type": "",
            "dateb": "",
            "owner": "include",
            "count": "1",
            "search_text": "",
            "output": "atom",
        }
        try:
            resp = self._get_request(url, params=params)
            # The Atom feed contains the CIK in the <CIK> tag or URL
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "lxml-xml")
            # Try the company-info accession approach
            cik_tag = soup.find("cik")
            if cik_tag:
                return cik_tag.text.strip().zfill(10)

            # Fallback: parse from link URLs
            link = soup.find("link", href=True)
            if link:
                href = link["href"]
                # URL pattern: .../edgar/data/XXXXXXXXXX/...
                parts = href.split("/")
                for i, part in enumerate(parts):
                    if part == "data" and i + 1 < len(parts):
                        return parts[i + 1].zfill(10)
        except Exception:
            logger.debug("Atom CIK lookup failed, trying JSON tickers file")

        # Fallback: use the SEC's JSON tickers mapping
        try:
            resp = self._get_request("https://www.sec.gov/files/company_tickers.json")
            data = resp.json()
            for entry in data.values():
                if entry.get("ticker", "").upper() == self.ticker:
                    return str(entry["cik_str"]).zfill(10)
        except Exception:
            logger.debug("JSON tickers CIK lookup also failed for %s", self.ticker)

        return None

    def _get_request(self, url: str, **kwargs):
        """Wrapper around session.get with timeout."""
        kwargs.setdefault("timeout", 15)
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

    def _fetch_filings(self, cik: str) -> list[SECFiling]:
        """Fetch recent filings from the EDGAR submissions API."""
        url = EDGAR_SUBMISSIONS_URL.format(cik=cik)
        try:
            resp = self._get_request(url)
            data = resp.json()
        except Exception as exc:
            logger.warning("Failed to fetch EDGAR submissions for CIK %s: %s", cik, exc)
            return []

        recent = data.get("filings", {}).get("recent", {})
        if not recent:
            return []

        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        descriptions = recent.get("primaryDocDescription", [])

        filings: list[SECFiling] = []
        for i, form_type in enumerate(forms):
            if form_type not in FILING_TYPES:
                continue
            if len(filings) >= MAX_FILINGS:
                break

            accession_clean = accessions[i].replace("-", "")
            doc_url = (
                f"{EDGAR_FILING_BASE_URL}/{cik.lstrip('0')}"
                f"/{accession_clean}/{primary_docs[i]}"
            )

            filings.append(
                SECFiling(
                    filing_type=form_type,
                    date=dates[i] if i < len(dates) else "",
                    description=descriptions[i] if i < len(descriptions) else form_type,
                    url=doc_url,
                )
            )

        return filings
