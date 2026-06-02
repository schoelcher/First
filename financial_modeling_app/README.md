# Local Financial Modeling Workbench

A private, local Streamlit app that turns a public-company ticker into a standardized historical model, five-year forecast, DCF valuation dashboard, sensitivity tables, and Excel export.

This is **Phase 1 only**: no authentication, no accounts, no SaaS infrastructure, no AI commentary, no comps, and no earnings-call analysis.

## Setup

```bash
cd financial_modeling_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

Use the Setup tab to enter a ticker and click **Build Model**. The app also includes a **Use Demo Data** toggle and will automatically fall back to demo data if external data fetching fails.

## Data sources

- **SEC EDGAR company facts**: primary historical financial source via `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`.
- **SEC ticker mapping**: maps ticker to CIK via `https://www.sec.gov/files/company_tickers.json`.
- **yfinance**: optional fallback for current share price, beta, market cap, shares outstanding, cash, and debt. If yfinance fails, the app still runs and lets you override market inputs manually.

## SEC User-Agent

The SEC asks automated clients to identify themselves. Set `SEC_USER_AGENT` before running the app:

```bash
export SEC_USER_AGENT="Your Name your.email@example.com"
streamlit run app.py
```

If `SEC_USER_AGENT` is not set, the app uses a generic local-development User-Agent, but you should set your own for regular use.

## Example tickers

Try:

- `AAPL`
- `MSFT`
- `GOOGL`

Click **Build Model**, then adjust the sliders in the Assumptions tab. Forecasts, WACC, DCF valuation, implied share price, and sensitivities update immediately on rerun.

## Current limitations

- Annual 10-K / 10-K/A data only.
- Designed for standard non-financial public companies.
- Explicitly out of scope for v1: banks, insurers, REITs, BDCs, highly specialized biotech, and companies with insufficient standardized SEC data.
- SEC XBRL tags vary by issuer; fallback mappings are included, but some line items may still be missing or estimated.
- Excel export writes values; formulas are not required for v1.
- Market data is best-effort and may be unavailable if yfinance changes or network calls fail.
- This is not investment advice and does not replace professional diligence.

## Testing

```bash
pytest
```

## Suggested next improvements

- Add quarterly data support.
- Add better industry/entity type detection for excluded categories.
- Add issuer-specific tag diagnostics.
- Add formula-based Excel exports.
- Add richer data quality scoring and audit trails.
- Add optional local saved scenarios without building accounts or SaaS infrastructure.
