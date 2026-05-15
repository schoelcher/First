# EquityScope – Equity Research Dashboard

A local web dashboard that streams a comprehensive equity research report for any stock ticker. Scrapes multiple sources concurrently using Playwright, fetches news from five APIs in parallel, and integrates Portfolio 123 factor data.

---

## Quick Start

```bash
# 1. Copy env template and add your API keys
cp .env.example .env
# Edit .env with your keys (see "API Keys" section below)

# 2. Install dependencies + Playwright browser
pip install -r requirements.txt
playwright install chromium

# 3. Run
python run_dashboard.py
# → http://localhost:8000
```

Or in one command:
```bash
bash setup_and_run.sh
```

### Expose via ngrok (optional)
```bash
ngrok http 8000
```

---

## Dashboard Data Sources

| Source | What it provides | Key required? |
|--------|-----------------|---------------|
| **Yahoo Finance (yfinance)** | Price, financials, analyst consensus, SEC filings | No |
| **Finviz** | 70+ metrics, RSI, short interest, insider %, institutional ownership, analyst ratings | No |
| **Yahoo Finance Analysis** | Earnings/revenue estimates, upgrades/downgrades | No |
| **OpenInsider** | Insider transactions with buy/sell sentiment | No |
| **Google News** | Premium articles (WSJ, Bloomberg, Reuters, FT, Barron's) | No |
| **Finnhub** | Company news (past 30 days) | `FINNHUB_API_KEY` |
| **NewsAPI** | Broad news search by ticker + company name | `NEWS_API_KEY` |
| **Alpha Vantage** | News with per-article sentiment scores | `ALPHA_VANTAGE_KEY` |
| **Reuters RSS** | Business news, filtered by ticker mention | No |
| **MarketWatch RSS** | Top stories, filtered by ticker mention | No |
| **Portfolio 123** | Factor scores: P/E, P/B, ROE, Piotroski, growth, etc. | `P123_API_ID` + `P123_API_KEY` |

---

## API Keys

All keys are **optional**. The dashboard works without any of them — sources with missing keys are skipped and labelled "Not configured" in the UI.

### Finnhub
1. Sign up at [finnhub.io](https://finnhub.io)
2. Dashboard → copy your API key
3. Set `FINNHUB_API_KEY=<your_key>` in `.env`

Free tier: 60 req/min, company news included.

### NewsAPI
1. Sign up at [newsapi.org](https://newsapi.org)
2. Copy your API key from the dashboard
3. Set `NEWS_API_KEY=<your_key>` in `.env`

Free tier: 100 req/day, articles up to 1 month old.

### Alpha Vantage
1. Get a free key at [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. Set `ALPHA_VANTAGE_KEY=<your_key>` in `.env`

Free tier: 25 req/day. Returns sentiment scores per article.

### Portfolio 123
1. Log in to [portfolio123.com](https://www.portfolio123.com)
2. Go to **Account → API Keys → Create Key**
3. Copy both your **API ID** (numeric) and **API Key** (UUID string)
4. Add to `.env`:
   ```
   P123_API_ID=<your_numeric_id>
   P123_API_KEY=<your_key_string>
   ```

The dashboard queries ~20 factor formulas per ticker (valuation, quality, growth, technicals).

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FINNHUB_API_KEY` | — | Finnhub news API key |
| `NEWS_API_KEY` | — | NewsAPI key |
| `ALPHA_VANTAGE_KEY` | — | Alpha Vantage key |
| `P123_API_ID` | — | Portfolio 123 numeric API ID |
| `P123_API_KEY` | — | Portfolio 123 API key |
| `DASHBOARD_PORT` | `8000` | Server port |
| `DASHBOARD_HOST` | `0.0.0.0` | Bind address |
| `DASHBOARD_CACHE_TTL_HOURS` | `4` | Cache TTL in hours |
| `DASHBOARD_HEADLESS` | `true` | Run browser headless |

---

## CLI Scraper

The original command-line scraper is still available:

```bash
pip install -e .
equity-research AAPL
equity-research AAPL --format json --output report.json
```

Available sections: `profile`, `financials`, `price`, `analysts`, `filings`, `news`

---

## Project Structure

```
dashboard/               ← Web dashboard
├── app.py               ← FastAPI app (SSE streaming)
├── config.py            ← Env var loading
├── database.py          ← SQLite cache
└── scrapers/
    ├── browser.py       ← Playwright browser singleton
    ├── finviz.py        ← Finviz snapshot + ratings
    ├── yahoo_analysis.py← Yahoo estimates + upgrades
    ├── openinsider.py   ← Insider transactions
    ├── news_search.py   ← Google News (Playwright)
    ├── news_apis.py     ← Finnhub / NewsAPI / AV / RSS (parallel)
    ├── portfolio123.py  ← Portfolio 123 factor data
    └── aggregator.py    ← Orchestrates all scrapers

equity_research/         ← Original CLI scraper
run_dashboard.py         ← Entry point
.env.example             ← API key template
```
