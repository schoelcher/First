"""Tests for the data models."""

import json

from equity_research.models import (
    AnalystData,
    CompanyProfile,
    EquityResearchReport,
    FinancialData,
    NewsItem,
    PriceData,
    SECFiling,
)


class TestCompanyProfile:
    def test_defaults(self):
        profile = CompanyProfile()
        assert profile.ticker == ""
        assert profile.name == ""
        assert profile.employees is None

    def test_with_values(self):
        profile = CompanyProfile(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Technology",
            employees=164000,
        )
        assert profile.ticker == "AAPL"
        assert profile.name == "Apple Inc."
        assert profile.employees == 164000


class TestFinancialData:
    def test_defaults_are_none(self):
        data = FinancialData()
        assert data.market_cap is None
        assert data.trailing_pe is None
        assert data.revenue is None

    def test_with_values(self):
        data = FinancialData(market_cap=3_000_000_000_000, trailing_pe=30.5)
        assert data.market_cap == 3_000_000_000_000
        assert data.trailing_pe == 30.5


class TestPriceData:
    def test_defaults(self):
        data = PriceData()
        assert data.current_price is None
        assert data.beta is None

    def test_with_values(self):
        data = PriceData(current_price=195.50, beta=1.25)
        assert data.current_price == 195.50
        assert data.beta == 1.25


class TestAnalystData:
    def test_defaults(self):
        data = AnalystData()
        assert data.recommendation == ""
        assert data.target_mean is None

    def test_with_values(self):
        data = AnalystData(recommendation="buy", target_mean=220.0, number_of_analysts=35)
        assert data.recommendation == "buy"
        assert data.target_mean == 220.0


class TestSECFiling:
    def test_creation(self):
        filing = SECFiling(
            filing_type="10-K",
            date="2024-10-31",
            description="Annual Report",
            url="https://sec.gov/filing/123",
        )
        assert filing.filing_type == "10-K"
        assert filing.date == "2024-10-31"


class TestNewsItem:
    def test_creation(self):
        item = NewsItem(
            title="Company beats earnings",
            link="https://news.example.com/article",
            published="Mon, 01 Jan 2024 12:00:00 +0000",
            source="Reuters",
        )
        assert item.title == "Company beats earnings"
        assert item.source == "Reuters"


class TestEquityResearchReport:
    def test_defaults(self):
        report = EquityResearchReport(ticker="AAPL")
        assert report.ticker == "AAPL"
        assert report.filings == []
        assert report.news == []
        assert report.errors == []

    def test_to_dict(self):
        report = EquityResearchReport(
            ticker="MSFT",
            profile=CompanyProfile(ticker="MSFT", name="Microsoft Corporation"),
        )
        d = report.to_dict()
        assert d["ticker"] == "MSFT"
        assert d["profile"]["name"] == "Microsoft Corporation"
        assert isinstance(d["filings"], list)

    def test_to_json(self):
        report = EquityResearchReport(
            ticker="GOOG",
            profile=CompanyProfile(ticker="GOOG", name="Alphabet Inc."),
            financials=FinancialData(market_cap=2_000_000_000_000),
        )
        json_str = report.to_json()
        parsed = json.loads(json_str)
        assert parsed["ticker"] == "GOOG"
        assert parsed["profile"]["name"] == "Alphabet Inc."
        assert parsed["financials"]["market_cap"] == 2_000_000_000_000

    def test_to_json_indent(self):
        report = EquityResearchReport(ticker="TEST")
        json_str = report.to_json(indent=4)
        # 4-space indented JSON should have "    " in the output
        assert '    "ticker"' in json_str
