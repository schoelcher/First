"""Report generation utilities for equity research data."""

from __future__ import annotations

from equity_research.models import EquityResearchReport


def _fmt_number(value, prefix: str = "", suffix: str = "", decimals: int = 2) -> str:
    """Format a numeric value for display, handling None gracefully."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{prefix}{value:,.{decimals}f}{suffix}"
    return f"{prefix}{value:,}{suffix}"


def _fmt_large_number(value) -> str:
    """Format large numbers with B/M/K suffixes."""
    if value is None:
        return "N/A"
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000_000_000:
        return f"${sign}{abs_val / 1_000_000_000_000:,.2f}T"
    if abs_val >= 1_000_000_000:
        return f"${sign}{abs_val / 1_000_000_000:,.2f}B"
    if abs_val >= 1_000_000:
        return f"${sign}{abs_val / 1_000_000:,.2f}M"
    if abs_val >= 1_000:
        return f"${sign}{abs_val / 1_000:,.2f}K"
    return f"${sign}{abs_val:,.2f}"


def _fmt_pct(value) -> str:
    """Format a decimal ratio as a percentage string."""
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def _section_header(title: str) -> str:
    return f"\n{'=' * 60}\n  {title}\n{'=' * 60}"


def generate_text_report(report: EquityResearchReport) -> str:
    """Generate a human-readable plain text report."""
    lines: list[str] = []
    p = report.profile
    f = report.financials
    pr = report.price
    a = report.analysts

    # Title
    name_display = p.name or report.ticker
    lines.append("=" * 60)
    lines.append(f"  EQUITY RESEARCH REPORT: {name_display} ({report.ticker})")
    lines.append("=" * 60)

    # Profile
    if p.name:
        lines.append(_section_header("COMPANY PROFILE"))
        lines.append(f"  Name:           {p.name}")
        lines.append(f"  Ticker:         {p.ticker}")
        lines.append(f"  Exchange:       {p.exchange}")
        lines.append(f"  Sector:         {p.sector}")
        lines.append(f"  Industry:       {p.industry}")
        lines.append(f"  Headquarters:   {p.headquarters}")
        lines.append(f"  Employees:      {_fmt_number(p.employees)}")
        lines.append(f"  Website:        {p.website}")
        if p.description:
            lines.append(f"\n  Description:\n  {p.description[:500]}")
            if len(p.description) > 500:
                lines.append("  ...")

    # Financials
    if f.market_cap is not None:
        lines.append(_section_header("FINANCIAL DATA"))
        lines.append(f"  Market Cap:         {_fmt_large_number(f.market_cap)}")
        lines.append(f"  Enterprise Value:   {_fmt_large_number(f.enterprise_value)}")
        lines.append(f"  Revenue:            {_fmt_large_number(f.revenue)}")
        lines.append(f"  Revenue Growth:     {_fmt_pct(f.revenue_growth)}")
        lines.append(f"  Trailing P/E:       {_fmt_number(f.trailing_pe)}")
        lines.append(f"  Forward P/E:        {_fmt_number(f.forward_pe)}")
        lines.append(f"  PEG Ratio:          {_fmt_number(f.peg_ratio)}")
        lines.append(f"  EPS:                {_fmt_number(f.earnings_per_share, prefix='$')}")
        lines.append(f"  Price/Book:         {_fmt_number(f.price_to_book)}")
        lines.append(f"  Price/Sales:        {_fmt_number(f.price_to_sales)}")
        lines.append("")
        lines.append(f"  Gross Margin:       {_fmt_pct(f.gross_margins)}")
        lines.append(f"  Operating Margin:   {_fmt_pct(f.operating_margins)}")
        lines.append(f"  Profit Margin:      {_fmt_pct(f.profit_margins)}")
        lines.append(f"  ROE:                {_fmt_pct(f.return_on_equity)}")
        lines.append(f"  ROA:                {_fmt_pct(f.return_on_assets)}")
        lines.append("")
        lines.append(f"  Debt/Equity:        {_fmt_number(f.debt_to_equity)}")
        lines.append(f"  Current Ratio:      {_fmt_number(f.current_ratio)}")
        lines.append(f"  Book Value:         {_fmt_number(f.book_value, prefix='$')}")
        lines.append(f"  Total Cash:         {_fmt_large_number(f.total_cash)}")
        lines.append(f"  Total Debt:         {_fmt_large_number(f.total_debt)}")
        lines.append(f"  Free Cash Flow:     {_fmt_large_number(f.free_cash_flow)}")
        lines.append("")
        lines.append(f"  Dividend Yield:     {_fmt_pct(f.dividend_yield)}")
        lines.append(f"  Dividend Rate:      {_fmt_number(f.dividend_rate, prefix='$')}")
        lines.append(f"  Payout Ratio:       {_fmt_pct(f.payout_ratio)}")

    # Price
    if pr.current_price is not None:
        lines.append(_section_header("PRICE & TRADING"))
        lines.append(f"  Current Price:      {_fmt_number(pr.current_price, prefix='$')}")
        lines.append(f"  Previous Close:     {_fmt_number(pr.previous_close, prefix='$')}")
        lines.append(f"  Open:               {_fmt_number(pr.open_price, prefix='$')}")
        lines.append(f"  Day Range:          {_fmt_number(pr.day_low, prefix='$')} - {_fmt_number(pr.day_high, prefix='$')}")
        lines.append(f"  52-Week Range:      {_fmt_number(pr.fifty_two_week_low, prefix='$')} - {_fmt_number(pr.fifty_two_week_high, prefix='$')}")
        lines.append(f"  50-Day Avg:         {_fmt_number(pr.fifty_day_average, prefix='$')}")
        lines.append(f"  200-Day Avg:        {_fmt_number(pr.two_hundred_day_average, prefix='$')}")
        lines.append(f"  Volume:             {_fmt_number(pr.volume)}")
        lines.append(f"  Avg Volume:         {_fmt_number(pr.average_volume)}")
        lines.append(f"  Beta:               {_fmt_number(pr.beta)}")

    # Analysts
    if a.target_mean is not None or a.recommendation:
        lines.append(_section_header("ANALYST COVERAGE"))
        lines.append(f"  Recommendation:     {a.recommendation.upper() if a.recommendation else 'N/A'}")
        lines.append(f"  # of Analysts:      {_fmt_number(a.number_of_analysts)}")
        lines.append(f"  Target (Mean):      {_fmt_number(a.target_mean, prefix='$')}")
        lines.append(f"  Target (Median):    {_fmt_number(a.target_median, prefix='$')}")
        lines.append(f"  Target (High):      {_fmt_number(a.target_high, prefix='$')}")
        lines.append(f"  Target (Low):       {_fmt_number(a.target_low, prefix='$')}")

    # SEC Filings
    if report.filings:
        lines.append(_section_header("SEC FILINGS (Recent)"))
        for filing in report.filings:
            lines.append(f"  [{filing.filing_type}] {filing.date}  {filing.description}")
            lines.append(f"    {filing.url}")

    # News
    if report.news:
        lines.append(_section_header("RECENT NEWS"))
        for item in report.news:
            source_str = f" ({item.source})" if item.source else ""
            lines.append(f"  - {item.title}{source_str}")
            lines.append(f"    {item.published}")
            if item.link:
                lines.append(f"    {item.link}")

    # Errors
    if report.errors:
        lines.append(_section_header("ERRORS"))
        for err in report.errors:
            lines.append(f"  ! {err}")

    lines.append("\n" + "=" * 60)
    lines.append("  End of Report")
    lines.append("=" * 60)

    return "\n".join(lines)


def generate_json_report(report: EquityResearchReport) -> str:
    """Generate a JSON-formatted report."""
    return report.to_json(indent=2)
