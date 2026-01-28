# Equity Research Web Scraper

A command-line tool that gathers comprehensive equity research data for any publicly traded company using its stock ticker symbol.

## Features

- **Company Profile**: Name, sector, industry, description, headquarters, employees, website
- **Financial Data**: Market cap, P/E ratio, EPS, revenue, profit margins, dividends, balance sheet metrics
- **Price & Trading**: Current price, 52-week range, volume, moving averages, beta
- **Analyst Coverage**: Price targets, recommendations, earnings estimates
- **SEC Filings**: Recent 10-K, 10-Q, and 8-K filings from EDGAR
- **News**: Latest financial news headlines and summaries
- **Report Export**: Generate reports in plain text or JSON format

## Data Sources

| Source | Data |
|---|---|
| Yahoo Finance (via `yfinance`) | Company profile, financials, price data, analyst estimates |
| SEC EDGAR | Regulatory filings (10-K, 10-Q, 8-K) |
| Yahoo Finance RSS | Latest news headlines |

## Installation

```bash
pip install -e ".[dev]"
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Usage

### Basic lookup
```bash
python -m equity_research AAPL
```

### Specify output format
```bash
python -m equity_research AAPL --format json
python -m equity_research AAPL --format text
```

### Save report to file
```bash
python -m equity_research AAPL --output report.json --format json
python -m equity_research AAPL --output report.txt --format text
```

### Select specific sections
```bash
python -m equity_research AAPL --sections profile financials price
```

Available sections: `profile`, `financials`, `price`, `analysts`, `filings`, `news`

## Project Structure

```
equity_research/
├── __init__.py
├── models.py           # Data models (dataclasses)
├── scrapers/
│   ├── __init__.py
│   ├── base.py         # Abstract base scraper
│   ├── yahoo_finance.py# Yahoo Finance data via yfinance
│   ├── sec_edgar.py    # SEC EDGAR filings
│   └── news.py         # Financial news scraper
├── aggregator.py       # Orchestrates all scrapers
├── report.py           # Report generation (text/JSON)
└── cli.py              # Command-line interface
```

## Development

Run tests:
```bash
pytest
```

## License

MIT
