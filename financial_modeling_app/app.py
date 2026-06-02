"""Local Streamlit financial modeling and DCF valuation workbench."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.market_data import fetch_market_data
from src.data.sec_client import fetch_normalized_financials
from src.export.excel_export import export_model_to_excel
from src.model.assumptions import ModelAssumptions, build_default_assumptions
from src.model.dcf import calculate_dcf
from src.model.forecast import generate_forecast
from src.model.normalized_financials import demo_financials
from src.model.sensitivity import build_sensitivity_tables
from src.model.wacc import calculate_wacc
from src.utils.formatting import format_currency, format_multiple, format_number, format_percent
from src.utils.validation import scope_warning, validate_assumptions, validate_dcf_result, validate_historical_financials

st.set_page_config(page_title="Local Financial Modeling Workbench", layout="wide")
st.title("Local Financial Modeling Workbench")
st.caption("Phase 1: ticker → SEC historicals → forecast → DCF → sensitivity → Excel export")


def _load_model(ticker: str, use_demo: bool) -> None:
    warnings: list[str] = []
    if use_demo:
        historical, metadata, demo_warnings = demo_financials()
        market, market_warnings = fetch_market_data(ticker) if ticker and ticker != "DEMO" else ({}, [])
        warnings.extend(demo_warnings + market_warnings)
    else:
        try:
            historical, metadata, sec_warnings = fetch_normalized_financials(ticker)
            market, market_warnings = fetch_market_data(ticker)
            warnings.extend(sec_warnings + market_warnings)
        except Exception as exc:  # noqa: BLE001 - explicit UI fallback.
            st.error(f"Could not fetch public data for {ticker}: {exc}")
            st.info("Loading demo data so the app remains usable. Toggle 'Use Demo Data' to force demo mode.")
            historical, metadata, demo_warnings = demo_financials()
            market = {}
            warnings.extend([f"External data fetch failed for {ticker}: {exc}"] + demo_warnings)
    warnings.extend(scope_warning(metadata.get("ticker", ticker), metadata.get("company_name", "")))
    warnings.extend(validate_historical_financials(historical))
    st.session_state["historical"] = historical
    st.session_state["metadata"] = metadata
    st.session_state["market"] = market
    st.session_state["warnings"] = warnings
    st.session_state["base_assumptions"] = build_default_assumptions(historical, market)


with st.sidebar:
    st.header("Setup")
    ticker_input = st.text_input("Ticker", value=st.session_state.get("ticker", "AAPL")).upper().strip()
    use_demo_data = st.toggle("Use Demo Data", value=False)
    if st.button("Build Model", type="primary") or "historical" not in st.session_state:
        st.session_state["ticker"] = ticker_input or "DEMO"
        _load_model(st.session_state["ticker"], use_demo_data)

historical: pd.DataFrame = st.session_state["historical"]
metadata: dict = st.session_state["metadata"]
market: dict = st.session_state.get("market", {})
warnings: list[str] = list(st.session_state.get("warnings", []))
base: ModelAssumptions = st.session_state["base_assumptions"]

with st.sidebar:
    st.header("Manual Overrides")
    latest = historical.iloc[-1]
    current_share_price = st.number_input("Current share price", min_value=0.0, value=float(base.current_share_price or 100.0), step=1.0)
    diluted_shares = st.number_input("Diluted shares outstanding", min_value=0.0, value=float(base.diluted_shares_outstanding or latest.get("diluted_shares_outstanding") or 1.0), step=1.0)
    cash = st.number_input("Cash", min_value=0.0, value=float(latest.get("cash_and_equivalents") or market.get("cash") or 0.0), step=100.0)
    debt = st.number_input("Debt", min_value=0.0, value=float(latest.get("total_debt") or market.get("total_debt") or 0.0), step=100.0)
    net_debt = st.number_input("Net debt", value=float(debt - cash), step=100.0)

tab_setup, tab_hist, tab_assump, tab_forecast, tab_valuation, tab_sens, tab_export = st.tabs(
    ["Setup", "Historical Financials", "Assumptions", "Forecast", "Valuation", "Sensitivity", "Export"]
)

with tab_assump:
    st.subheader("Operating Assumptions")
    c1, c2, c3 = st.columns(3)
    revenue_growth = c1.slider("Revenue growth", -20.0, 40.0, float(base.revenue_growth * 100), 0.5) / 100
    ebit_margin = c2.slider("EBIT margin", -20.0, 60.0, float(base.ebit_margin * 100), 0.5) / 100
    ebitda_margin = c3.slider("EBITDA margin", -20.0, 70.0, float(base.ebitda_margin * 100), 0.5) / 100
    da_percent_revenue = c1.slider("D&A / revenue", 0.0, 20.0, float(base.da_percent_revenue * 100), 0.25) / 100
    capex_percent_revenue = c2.slider("Capex / revenue", 0.0, 30.0, float(base.capex_percent_revenue * 100), 0.25) / 100
    nwc_percent_revenue = c3.slider("NWC / revenue", -20.0, 40.0, float(base.nwc_percent_revenue * 100), 0.5) / 100
    tax_rate = c1.slider("Tax rate", 0.0, 40.0, float(base.tax_rate * 100), 0.5) / 100

    st.subheader("Capital Costs")
    c1, c2, c3 = st.columns(3)
    risk_free_rate = c1.slider("Risk-free rate", 0.0, 10.0, float(base.risk_free_rate * 100), 0.1) / 100
    equity_risk_premium = c2.slider("Equity risk premium", 2.0, 10.0, float(base.equity_risk_premium * 100), 0.1) / 100
    beta = c3.slider("Beta", 0.3, 3.0, float(base.beta), 0.05)
    pre_tax_cost_of_debt = c1.slider("Pre-tax cost of debt", 0.0, 15.0, float(base.pre_tax_cost_of_debt * 100), 0.1) / 100
    debt_to_capital = c2.slider("Debt / capital", 0.0, 80.0, float(base.debt_to_capital * 100), 1.0) / 100
    equity_to_capital = 1 - debt_to_capital
    c3.metric("Equity / capital", format_percent(equity_to_capital))

    st.subheader("Valuation")
    c1, c2, c3 = st.columns(3)
    terminal_growth_rate = c1.slider("Terminal growth rate", 0.0, 6.0, float(base.terminal_growth_rate * 100), 0.1) / 100
    exit_ebitda_multiple = c2.slider("Exit EBITDA multiple", 2.0, 40.0, float(base.exit_ebitda_multiple), 0.5)
    terminal_label = c3.radio("Terminal method", ["Gordon Growth", "Exit Multiple"], horizontal=False)
    terminal_method = "gordon_growth" if terminal_label == "Gordon Growth" else "exit_multiple"

assumptions = ModelAssumptions(
    revenue_growth=revenue_growth,
    ebit_margin=ebit_margin,
    ebitda_margin=ebitda_margin,
    da_percent_revenue=da_percent_revenue,
    capex_percent_revenue=capex_percent_revenue,
    nwc_percent_revenue=nwc_percent_revenue,
    tax_rate=tax_rate,
    risk_free_rate=risk_free_rate,
    equity_risk_premium=equity_risk_premium,
    beta=beta,
    pre_tax_cost_of_debt=pre_tax_cost_of_debt,
    debt_to_capital=debt_to_capital,
    equity_to_capital=equity_to_capital,
    terminal_growth_rate=terminal_growth_rate,
    exit_ebitda_multiple=exit_ebitda_multiple,
    terminal_method=terminal_method,
    current_share_price=current_share_price,
    net_debt=net_debt,
    diluted_shares_outstanding=diluted_shares,
)
forecast = generate_forecast(historical, assumptions)
wacc_result = calculate_wacc(
    assumptions.risk_free_rate,
    assumptions.equity_risk_premium,
    assumptions.beta,
    assumptions.pre_tax_cost_of_debt,
    assumptions.tax_rate,
    assumptions.debt_to_capital,
    assumptions.equity_to_capital,
)
warnings.extend(validate_assumptions(wacc_result.wacc, assumptions.terminal_growth_rate, assumptions.debt_to_capital, assumptions.equity_to_capital))
try:
    dcf_result = calculate_dcf(
        forecast,
        wacc_result.wacc,
        assumptions.terminal_growth_rate,
        assumptions.exit_ebitda_multiple,
        assumptions.terminal_method,
        assumptions.net_debt,
        assumptions.diluted_shares_outstanding or 0,
        assumptions.current_share_price,
    )
    warnings.extend(validate_dcf_result(dcf_result.to_dict()))
except ValueError as exc:
    dcf_result = None
    warnings.append(str(exc))

sensitivity_tables = build_sensitivity_tables(historical, forecast, assumptions, wacc_result.wacc)

with tab_setup:
    st.subheader("Company Setup")
    st.write(f"**Ticker:** {metadata.get('ticker', st.session_state.get('ticker'))}")
    st.write(f"**Company:** {metadata.get('company_name', 'Unknown')}")
    st.write(f"**CIK:** {metadata.get('cik', 'Unknown')}")
    st.subheader("Market Data")
    st.json(market)
    if warnings:
        st.subheader("Warnings / Data Quality Notes")
        for warning in dict.fromkeys(warnings):
            st.warning(warning)

with tab_hist:
    st.subheader("Normalized Historical Financials")
    st.dataframe(historical, use_container_width=True)
    margins = pd.DataFrame(index=historical.index)
    margins["revenue_growth"] = historical["revenue"].pct_change()
    margins["gross_margin"] = historical["gross_profit"] / historical["revenue"]
    margins["operating_margin"] = historical["operating_income"] / historical["revenue"]
    margins["fcf_margin"] = historical["free_cash_flow"] / historical["revenue"]
    st.subheader("Margins and Growth")
    st.dataframe(margins, use_container_width=True)
    for col, title in [("revenue", "Revenue History"), ("operating_income", "Operating Income History"), ("free_cash_flow", "Free Cash Flow History")]:
        if col in historical:
            st.plotly_chart(px.line(historical.reset_index(), x="fiscal_year", y=col, markers=True, title=title), use_container_width=True)

with tab_forecast:
    st.subheader("Forecast Model")
    st.dataframe(forecast, use_container_width=True)
    for col, title in [("revenue", "Revenue Forecast"), ("ebit", "EBIT Forecast"), ("ebitda", "EBITDA Forecast"), ("unlevered_fcf", "Unlevered FCF Forecast")]:
        st.plotly_chart(px.line(forecast.reset_index(), x="fiscal_year", y=col, markers=True, title=title), use_container_width=True)

with tab_valuation:
    st.subheader("Valuation")
    if dcf_result is None:
        st.error("Valuation could not be calculated. Review warnings and assumptions.")
    else:
        dcf = dcf_result.to_dict()
        cols = st.columns(5)
        cols[0].metric("Current share price", format_currency(dcf["current_share_price"]))
        cols[1].metric("Implied share price", format_currency(dcf["implied_share_price"]))
        cols[2].metric("Upside/downside", format_percent(dcf["upside_downside"]))
        cols[3].metric("Enterprise value", format_currency(dcf["enterprise_value"]))
        cols[4].metric("Equity value", format_currency(dcf["equity_value"]))
        cols = st.columns(4)
        cols[0].metric("WACC", format_percent(wacc_result.wacc))
        cols[1].metric("Cost of equity", format_percent(wacc_result.cost_of_equity))
        cols[2].metric("After-tax cost of debt", format_percent(wacc_result.after_tax_cost_of_debt))
        cols[3].metric("Terminal value % of EV", format_percent(dcf["terminal_value_percent_of_ev"]))
        if dcf["terminal_value_percent_of_ev"] > 0.85:
            st.warning("Terminal value % of EV is above 85%.")
        st.subheader("DCF Bridge")
        st.dataframe(pd.DataFrame([dcf]).T.rename(columns={0: "value"}), use_container_width=True)
        st.subheader("Forecast FCF Table")
        st.dataframe(forecast[["unlevered_fcf", "ebitda"]], use_container_width=True)
        st.subheader("Terminal Value Calculation")
        st.write(f"Method: **{assumptions.terminal_method}**; terminal value: **{format_currency(dcf['terminal_value'])}**; PV terminal value: **{format_currency(dcf['pv_terminal_value'])}**")

with tab_sens:
    st.subheader("Sensitivity Tables (Implied Share Price)")
    for title, key in [("WACC vs Terminal Growth", "wacc_terminal_growth"), ("WACC vs Exit EBITDA Multiple", "wacc_exit_multiple"), ("Revenue Growth vs EBITDA Margin", "revenue_growth_ebitda_margin")]:
        st.write(f"**{title}**")
        st.dataframe(sensitivity_tables[key].style.format("${:,.2f}"), use_container_width=True)

with tab_export:
    st.subheader("Excel Export")
    if dcf_result is None:
        st.warning("Fix valuation errors before exporting.")
    else:
        excel_bytes = export_model_to_excel(
            metadata.get("ticker", st.session_state.get("ticker", "")),
            metadata.get("company_name", "Unknown"),
            historical,
            assumptions,
            forecast,
            wacc_result,
            dcf_result,
            sensitivity_tables,
            list(dict.fromkeys(warnings)),
        )
        st.download_button("Download Excel model", excel_bytes, file_name=f"{metadata.get('ticker', 'model')}_financial_model.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
