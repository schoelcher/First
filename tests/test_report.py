"""Tests for the report generation module."""

from equity_research.models import (
    AnalystData,
    CompanyProfile,
    EquityResearchReport,
    FinancialData,
    NewsItem,
    PriceData,
    SECFiling,
)
from equity_research.report import (
    _fmt_large_number,
    _fmt_number,
    _fmt_pct,
    generate_json_report,
    generate_text_report,
)


class TestFormatHelpers:
    def test_fmt_number_none(self):
        assert _fmt_number(None) == "N/A"

    def test_fmt_number_float(self):
        assert _fmt_number(30.5) == "30.50"

    def test_fmt_number_with_prefix(self):
        assert _fmt_number(195.5, prefix="$") == "$195.50"

    def test_fmt_number_int(self):
        assert _fmt_number(164000) == "164,000"

    def test_fmt_large_number_none(self):
        assert _fmt_large_number(None) == "N/A"

    def test_fmt_large_number_trillion(self):
        assert _fmt_large_number(3_000_000_000_000) == "$3.00T"

    def test_fmt_large_number_billion(self):
        assert _fmt_large_number(150_000_000_000) == "$150.00B"

    def test_fmt_large_number_million(self):
        assert _fmt_large_number(500_000_000) == "$500.00M"

    def test_fmt_large_number_thousand(self):
        assert _fmt_large_number(50_000) == "$50.00K"

    def test_fmt_large_number_small(self):
        assert _fmt_large_number(999) == "$999.00"

    def test_fmt_large_number_negative(self):
        assert _fmt_large_number(-2_000_000_000) == "$-2.00B"

    def test_fmt_pct_none(self):
        assert _fmt_pct(None) == "N/A"

    def test_fmt_pct_value(self):
        assert _fmt_pct(0.2534) == "25.34%"


class TestGenerateTextReport:
    def _make_full_report(self) -> EquityResearchReport:
        return EquityResearchReport(
            ticker="AAPL",
            profile=CompanyProfile(
                ticker="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry="Consumer Electronics",
                headquarters="Cupertino, CA",
                employees=164000,
                exchange="NMS",
                website="https://apple.com",
                description="Apple designs and sells consumer electronics.",
            ),
            financials=FinancialData(
                market_cap=3_000_000_000_000,
                trailing_pe=30.5,
                revenue=400_000_000_000,
                profit_margins=0.26,
            ),
            price=PriceData(
                current_price=195.50,
                fifty_two_week_low=140.0,
                fifty_two_week_high=200.0,
                beta=1.25,
            ),
            analysts=AnalystData(
                recommendation="buy",
                target_mean=210.0,
                number_of_analysts=35,
            ),
            filings=[
                SECFiling(
                    filing_type="10-K",
                    date="2024-10-31",
                    description="Annual Report",
                    url="https://sec.gov/filing/123",
                )
            ],
            news=[
                NewsItem(
                    title="Apple beats earnings",
                    link="https://news.example.com/1",
                    published="2024-01-01",
                    source="Reuters",
                )
            ],
        )

    def test_text_report_contains_ticker(self):
        report = self._make_full_report()
        text = generate_text_report(report)
        assert "AAPL" in text

    def test_text_report_contains_company_name(self):
        report = self._make_full_report()
        text = generate_text_report(report)
        assert "Apple Inc." in text

    def test_text_report_contains_sections(self):
        report = self._make_full_report()
        text = generate_text_report(report)
        assert "COMPANY PROFILE" in text
        assert "FINANCIAL DATA" in text
        assert "PRICE & TRADING" in text
        assert "ANALYST COVERAGE" in text
        assert "SEC FILINGS" in text
        assert "RECENT NEWS" in text

    def test_text_report_contains_financial_data(self):
        report = self._make_full_report()
        text = generate_text_report(report)
        assert "$3.00T" in text
        assert "30.50" in text

    def test_text_report_contains_news(self):
        report = self._make_full_report()
        text = generate_text_report(report)
        assert "Apple beats earnings" in text
        assert "Reuters" in text

    def test_text_report_empty_report(self):
        report = EquityResearchReport(ticker="EMPTY")
        text = generate_text_report(report)
        assert "EMPTY" in text
        assert "End of Report" in text


class TestGenerateJsonReport:
    def test_json_report_is_valid_json(self):
        import json

        report = EquityResearchReport(
            ticker="TEST",
            profile=CompanyProfile(ticker="TEST", name="Test Corp"),
        )
        output = generate_json_report(report)
        parsed = json.loads(output)
        assert parsed["ticker"] == "TEST"
        assert parsed["profile"]["name"] == "Test Corp"
