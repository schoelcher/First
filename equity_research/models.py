"""Data models for equity research information."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class CompanyProfile:
    """Basic company identification and description."""

    ticker: str = ""
    name: str = ""
    sector: str = ""
    industry: str = ""
    description: str = ""
    website: str = ""
    headquarters: str = ""
    employees: Optional[int] = None
    exchange: str = ""
    currency: str = ""


@dataclass
class FinancialData:
    """Key financial metrics and ratios."""

    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    earnings_per_share: Optional[float] = None
    revenue: Optional[float] = None
    revenue_growth: Optional[float] = None
    gross_margins: Optional[float] = None
    operating_margins: Optional[float] = None
    profit_margins: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None
    dividend_yield: Optional[float] = None
    dividend_rate: Optional[float] = None
    payout_ratio: Optional[float] = None
    book_value: Optional[float] = None
    total_cash: Optional[float] = None
    total_debt: Optional[float] = None


@dataclass
class PriceData:
    """Current price and trading information."""

    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    day_low: Optional[float] = None
    day_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_day_average: Optional[float] = None
    two_hundred_day_average: Optional[float] = None
    volume: Optional[int] = None
    average_volume: Optional[int] = None
    beta: Optional[float] = None


@dataclass
class AnalystData:
    """Analyst estimates and recommendations."""

    target_high: Optional[float] = None
    target_low: Optional[float] = None
    target_mean: Optional[float] = None
    target_median: Optional[float] = None
    recommendation: str = ""
    number_of_analysts: Optional[int] = None
    earnings_estimate_current_qtr: Optional[float] = None
    earnings_estimate_next_qtr: Optional[float] = None
    revenue_estimate_current_qtr: Optional[float] = None
    revenue_estimate_next_qtr: Optional[float] = None


@dataclass
class SECFiling:
    """A single SEC filing record."""

    filing_type: str = ""
    date: str = ""
    description: str = ""
    url: str = ""


@dataclass
class NewsItem:
    """A single news article."""

    title: str = ""
    link: str = ""
    published: str = ""
    source: str = ""


@dataclass
class EquityResearchReport:
    """Complete equity research report aggregating all data sources."""

    ticker: str = ""
    profile: CompanyProfile = field(default_factory=CompanyProfile)
    financials: FinancialData = field(default_factory=FinancialData)
    price: PriceData = field(default_factory=PriceData)
    analysts: AnalystData = field(default_factory=AnalystData)
    filings: list[SECFiling] = field(default_factory=list)
    news: list[NewsItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert the report to a dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize the report to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
