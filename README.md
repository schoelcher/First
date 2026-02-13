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

## Flight-to-Uber Tasker (New)

This repository now also includes a lightweight `travel_tasker` module that automates airport transportation planning from flight data.

### What it does
- Reads your upcoming flights from a calendar provider abstraction (ready to wire to Google Calendar APIs).
- Classifies each flight as **local** or **international** based on country mismatch.
- Computes recommended airport arrival time:
  - local: 2 hours before departure
  - international: 3 hours before departure
  - adds an extra 30 minutes during rush-hour departure windows
- Estimates road travel time and calculates Uber pickup time with an additional 15-minute safety buffer.
- Schedules an **UberX** ride through an Uber provider abstraction.

### UX goal
You only provide a pickup location; the system derives the rest from flight + policy + transit estimates.

### Run demo CLI
```bash
travel-tasker --pickup-location "1600 Amphitheatre Parkway, Mountain View, CA"
travel-tasker --pickup-location "1600 Amphitheatre Parkway, Mountain View, CA" --dry-run
```

### Integration notes
Use concrete provider implementations for production:
- `CalendarProvider`: Google Calendar API adapter
- `TransitEstimator`: maps/traffic-time adapter
- `UberProvider`: Uber scheduling adapter
