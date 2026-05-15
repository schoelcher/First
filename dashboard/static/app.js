/* EquityScope v2 – Dashboard Frontend */

// ─── Helpers ───────────────────────────────────────────────────────────────

const $ = sel => document.querySelector(sel);
const $$ = sel => [...document.querySelectorAll(sel)];
const show = el => el.classList.remove('hidden');
const hide = el => el.classList.add('hidden');
const esc = s => { const d = document.createElement('div'); d.textContent = String(s ?? ''); return d.innerHTML; };

function fmt(n) {
  if (n == null || n === '' || n === 'N/A' || n === 'n/a') return '—';
  const num = Number(n);
  if (isNaN(num)) return esc(n);
  return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
}
function fmtLarge(n) {
  if (n == null) return '—';
  const v = Number(n); if (isNaN(v)) return String(n);
  const a = Math.abs(v);
  if (a >= 1e12) return (v/1e12).toFixed(2) + 'T';
  if (a >= 1e9)  return (v/1e9).toFixed(2)  + 'B';
  if (a >= 1e6)  return (v/1e6).toFixed(2)  + 'M';
  if (a >= 1e3)  return (v/1e3).toFixed(1)  + 'K';
  return fmt(v);
}
function fmtPct(n) {
  if (n == null || n === '') return '—';
  const v = Number(n); if (isNaN(v)) return String(n);
  if (Math.abs(v) < 1 && v !== 0) return (v*100).toFixed(2) + '%';
  return v.toFixed(2) + '%';
}
function fmtPrice(n) { return n == null ? '—' : '$' + Number(n).toFixed(2); }
function fmtP123(val, fmt_hint) {
  if (val == null || val === '' || val === 'N/A') return '—';
  const v = Number(val);
  if (isNaN(v)) return esc(val);
  if (fmt_hint === 'price')  return '$' + v.toFixed(2);
  if (fmt_hint === 'pct')    return v.toFixed(2) + '%';
  if (fmt_hint === 'int')    return Math.round(v).toString();
  if (fmt_hint === 'ratio')  return v.toFixed(2) + 'x';
  return v.toFixed(2);
}
function changeSign(n) { return Number(n) >= 0 ? '+' : ''; }
function clrChg(n)  { return Number(n) >= 0 ? 'clr-green' : 'clr-red'; }
function arrow(n)   { return Number(n) >= 0 ? '▲' : '▼'; }

function ratingClass(rec) {
  const r = (rec||'').toLowerCase().replace('_',' ');
  if (r.includes('strong buy') || r.includes('strongbuy')) return 'badge-green';
  if (r.includes('buy'))   return 'badge-green';
  if (r.includes('hold') || r.includes('neutral') || r.includes('equal')) return 'badge-yellow';
  if (r.includes('sell') || r.includes('under')) return 'badge-red';
  return 'badge-gray';
}

function actionClass(a) {
  const l = (a||'').toLowerCase();
  if (l.includes('upgrade'))   return 'badge-green';
  if (l.includes('downgrade')) return 'badge-red';
  if (l.includes('initiat'))   return 'badge-blue';
  if (l.includes('reiterat') || l.includes('maintain')) return 'badge-yellow';
  return 'badge-gray';
}

// Source badge for news
const SOURCE_CLASSES = {
  finnhub: 'src-finnhub', newsapi: 'src-newsapi', alphavantage: 'src-alphavantage',
  reuters: 'src-reuters', marketwatch: 'src-marketwatch', yahoo: 'src-yahoo',
  finviz: 'src-finviz', tier1: 'src-tier1', tier2: 'src-tier2',
};
function sourceBadge(sourceId, sourceName) {
  const cls = SOURCE_CLASSES[sourceId] || SOURCE_CLASSES[sourceId?.split('-')[0]] || 'badge-gray';
  return `<span class="badge ${cls}">${esc(sourceName || sourceId)}</span>`;
}
function sentimentBadge(s, score) {
  if (!s) return '';
  const icons = { positive: '▲', negative: '▼', neutral: '●' };
  const cls   = { positive: 'sentiment-positive', negative: 'sentiment-negative', neutral: 'sentiment-neutral' };
  const scoreStr = score != null ? ` ${Number(score).toFixed(2)}` : '';
  return `<span class="${cls[s] || ''}">${icons[s] || ''} ${s}${scoreStr}</span>`;
}

// ─── State ─────────────────────────────────────────────────────────────────

let baseData = null, finvizData = null, yahooAnalysis = null;
let insiderData = null, newsDeep = null, newsApis = null, p123Data = null;
let evtSource = null;

function resetState() {
  baseData = finvizData = yahooAnalysis = insiderData = newsDeep = newsApis = p123Data = null;
  $$('.card').forEach(c => { c.innerHTML = '<div class="card-skeleton"></div>'; });
}

// ─── SSE connection ─────────────────────────────────────────────────────────

function startResearch(ticker) {
  if (evtSource) evtSource.close();
  resetState();
  hide($('#welcome'));
  show($('#dashboard'));
  show($('#statusBar'));
  $('#statusText').textContent = 'Connecting…';

  evtSource = new EventSource(`/api/research/${encodeURIComponent(ticker)}`);
  evtSource.onmessage = e => {
    let msg; try { msg = JSON.parse(e.data); } catch { return; }

    if (msg.section === 'status') {
      $('#statusText').textContent = msg.data?.message || 'Working…';
    } else if (msg.section === 'done' || msg.status === 'complete') {
      evtSource.close(); evtSource = null; hide($('#statusBar'));
    } else {
      dispatch(msg);
    }
  };
  evtSource.onerror = () => { if (evtSource) { evtSource.close(); evtSource = null; } hide($('#statusBar')); };
}

function dispatch(msg) {
  switch (msg.section) {
    case 'base':           baseData = msg.data;    renderBase();         break;
    case 'finviz':         finvizData = msg.data;  renderFinviz();       break;
    case 'yahoo_analysis': yahooAnalysis = msg.data; renderYahoo();      break;
    case 'insider':        insiderData = msg.data; renderInsider();      break;
    case 'news_deep':      newsDeep = msg.data;    renderUnifiedNews();  break;
    case 'news_apis':      newsApis = msg.data;    renderUnifiedNews();  break;
    case 'portfolio123':   p123Data = msg.data;    renderP123();         break;
  }
}

$('#searchForm').addEventListener('submit', e => {
  e.preventDefault();
  const t = $('#tickerInput').value.trim().toUpperCase();
  if (t) { $('#tickerInput').value = t; startResearch(t); }
});

// ─── Render: Base Data ──────────────────────────────────────────────────────

function renderBase() {
  if (!baseData) return;
  renderCompanyHeader();
  renderKeyMetrics();
  renderAnalystConsensus();
  renderValuation();
  renderFinancials();
  renderSECFilings();
  renderUnifiedNews();   // render with RSS news even before API news arrives
}

function renderCompanyHeader() {
  const p = baseData.profile || {}, pr = baseData.price || {};
  const chg = pr.current_price && pr.previous_close ? pr.current_price - pr.previous_close : null;
  const chgPct = chg != null && pr.previous_close ? (chg / pr.previous_close) * 100 : null;
  const cc = chg != null ? clrChg(chg) : '';

  $('#companyHeader').innerHTML = `
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold text-white truncate">${esc(p.name || baseData.ticker)}</h2>
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-sm text-slate-400">
          <span class="font-mono font-bold text-blue-400">${esc(baseData.ticker)}</span>
          ${p.exchange ? `<span>${esc(p.exchange)}</span>` : ''}
          ${p.sector   ? `<span class="text-slate-500">&middot;</span><span>${esc(p.sector)}</span>` : ''}
          ${p.industry ? `<span class="text-slate-500">&middot;</span><span>${esc(p.industry)}</span>` : ''}
          ${p.employees ? `<span class="text-slate-500">&middot;</span><span>${Number(p.employees).toLocaleString()} employees</span>` : ''}
        </div>
        ${p.description ? `<p class="mt-3 text-sm text-slate-400 max-w-3xl line-clamp-3">${esc(p.description)}</p>` : ''}
        ${p.website ? `<a href="${esc(p.website)}" target="_blank" class="text-xs text-blue-400 hover:underline mt-1 inline-block">${esc(p.website)}</a>` : ''}
      </div>
      <div class="text-right shrink-0">
        <div class="text-3xl font-bold text-white">${fmtPrice(pr.current_price)}</div>
        ${chg != null ? `<div class="text-lg font-semibold ${cc}">${arrow(chg)} ${changeSign(chg)}${chg.toFixed(2)} (${changeSign(chgPct)}${chgPct.toFixed(2)}%)</div>` : ''}
        <div class="text-xs text-slate-500 mt-0.5">Prev close ${fmtPrice(pr.previous_close)}</div>
      </div>
    </div>`;
}

function renderKeyMetrics() {
  const f = baseData.financials || {}, pr = baseData.price || {};
  const m = finvizData?.metrics || {};
  const items = [
    ['Market Cap',   fmtLarge(f.market_cap)],
    ['P/E (TTM)',    fmt(f.trailing_pe)],
    ['P/E (Fwd)',    fmt(f.forward_pe)],
    ['EPS (TTM)',    fmtPrice(f.earnings_per_share)],
    ['PEG',         fmt(f.peg_ratio)],
    ['Beta',        fmt(pr.beta)],
    ['Div. Yield',  f.dividend_yield != null ? fmtPct(f.dividend_yield) : '—'],
    ['52W High',    fmtPrice(pr.fifty_two_week_high)],
    ['52W Low',     fmtPrice(pr.fifty_two_week_low)],
    ['Avg Volume',  fmtLarge(pr.average_volume)],
    ['50D MA',      fmtPrice(pr.fifty_day_average)],
    ['200D MA',     fmtPrice(pr.two_hundred_day_average)],
    ...(m['RSI (14)'] ? [['RSI (14)', m['RSI (14)']]] : []),
    ...(m['ATR (14)'] ? [['ATR (14)', m['ATR (14)']]] : []),
    ...(m['Recom.']   ? [['Finviz Rec.', m['Recom.']]] : []),
    ...(m['Target Price'] ? [['Price Target', m['Target Price']]] : []),
  ];

  let rangeBar = '';
  const lo = pr.fifty_two_week_low, hi = pr.fifty_two_week_high, cur = pr.current_price;
  if (lo && hi && cur) {
    const pct = Math.max(0, Math.min(100, ((cur-lo)/(hi-lo))*100));
    rangeBar = `
      <div class="mt-4">
        <div class="flex justify-between text-xs text-slate-500 mb-1">
          <span>${fmtPrice(lo)}</span>
          <span class="text-slate-400 font-semibold">52-Week Range</span>
          <span>${fmtPrice(hi)}</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:100%"></div>
          <div class="bar-marker" style="left:${pct}%"></div>
        </div>
      </div>`;
  }

  $('#keyMetrics').innerHTML = `
    <div class="card-title">Key Metrics</div>
    <div class="metric-grid">${items.map(([l,v]) =>
      `<div class="metric-item"><div class="metric-label">${esc(l)}</div><div class="metric-value">${v}</div></div>`
    ).join('')}</div>${rangeBar}`;
}

function renderAnalystConsensus() {
  const a = baseData.analysts || {};
  const m = finvizData?.metrics || {};
  const rec = (a.recommendation || m['Recom.'] || '').replace('_',' ');
  const numA = a.number_of_analysts;
  const cur = baseData.price?.current_price;

  let targetHtml = '';
  if (a.target_mean != null) {
    const upside = cur ? ((a.target_mean - cur)/cur*100) : null;
    const upsideStr = upside != null
      ? `<span class="${clrChg(upside)}">(${changeSign(upside)}${upside.toFixed(1)}%)</span>` : '';
    let bar = '';
    if (a.target_low && a.target_high && cur) {
      const range = a.target_high - a.target_low;
      const cp = range > 0 ? Math.max(0,Math.min(100,((cur-a.target_low)/range)*100)) : 50;
      const mp = range > 0 ? Math.max(0,Math.min(100,((a.target_mean-a.target_low)/range)*100)) : 50;
      bar = `<div class="mt-3">
        <div class="flex justify-between text-xs text-slate-500 mb-1">
          <span>Low ${fmtPrice(a.target_low)}</span><span>High ${fmtPrice(a.target_high)}</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:100%"></div>
          <div class="bar-marker" style="left:${cp}%; background:#60a5fa" title="Current"></div>
          <div class="bar-marker" style="left:${mp}%; background:#fbbf24" title="Mean target"></div>
        </div>
        <div class="flex justify-between text-xs mt-1">
          <span class="text-blue-400">■ Current</span><span class="text-yellow-400">■ Mean Target</span>
        </div>
      </div>`;
    }
    targetHtml = `
      <div class="grid grid-cols-3 gap-3 mt-4">
        <div class="metric-item"><div class="metric-label">Target Low</div><div class="metric-value">${fmtPrice(a.target_low)}</div></div>
        <div class="metric-item"><div class="metric-label">Target Mean</div><div class="metric-value">${fmtPrice(a.target_mean)} ${upsideStr}</div></div>
        <div class="metric-item"><div class="metric-label">Target High</div><div class="metric-value">${fmtPrice(a.target_high)}</div></div>
      </div>${bar}`;
  }

  $('#analystConsensus').innerHTML = `
    <div class="card-title">Analyst Consensus</div>
    <div class="flex items-center gap-3 flex-wrap">
      <span class="badge ${ratingClass(rec)} text-sm px-4 py-1">${esc(rec || 'N/A')}</span>
      ${numA ? `<span class="text-sm text-slate-400">${numA} analyst${numA>1?'s':''}</span>` : ''}
    </div>
    ${targetHtml}`;
}

function renderValuation() {
  const f = baseData.financials || {};
  const items = [
    ['Enterprise Value', fmtLarge(f.enterprise_value)],
    ['P/E (TTM)',       fmt(f.trailing_pe)],
    ['P/E (Forward)',   fmt(f.forward_pe)],
    ['PEG Ratio',       fmt(f.peg_ratio)],
    ['Price / Book',    fmt(f.price_to_book)],
    ['Price / Sales',   fmt(f.price_to_sales)],
    ['Book Value/sh',   fmtPrice(f.book_value)],
    ['Debt / Equity',   fmt(f.debt_to_equity)],
  ];
  $('#valuation').innerHTML = `
    <div class="card-title">Valuation</div>
    <div class="metric-grid">${items.map(([l,v]) =>
      `<div class="metric-item"><div class="metric-label">${esc(l)}</div><div class="metric-value">${v}</div></div>`
    ).join('')}</div>`;
}

function renderFinancials() {
  const f = baseData.financials || {};
  const items = [
    ['Revenue',           fmtLarge(f.revenue)],
    ['Revenue Growth',    f.revenue_growth != null ? fmtPct(f.revenue_growth) : '—'],
    ['Gross Margin',      f.gross_margins  != null ? fmtPct(f.gross_margins)  : '—'],
    ['Operating Margin',  f.operating_margins != null ? fmtPct(f.operating_margins) : '—'],
    ['Profit Margin',     f.profit_margins != null ? fmtPct(f.profit_margins) : '—'],
    ['ROE',               f.return_on_equity != null ? fmtPct(f.return_on_equity)   : '—'],
    ['ROA',               f.return_on_assets != null ? fmtPct(f.return_on_assets)   : '—'],
    ['Free Cash Flow',    fmtLarge(f.free_cash_flow)],
    ['Total Cash',        fmtLarge(f.total_cash)],
    ['Total Debt',        fmtLarge(f.total_debt)],
    ['Current Ratio',     fmt(f.current_ratio)],
    ['Payout Ratio',      f.payout_ratio != null ? fmtPct(f.payout_ratio) : '—'],
  ];
  $('#financials').innerHTML = `
    <div class="card-title">Financials</div>
    <div class="metric-grid">${items.map(([l,v]) =>
      `<div class="metric-item"><div class="metric-label">${esc(l)}</div><div class="metric-value">${v}</div></div>`
    ).join('')}</div>`;
}

function renderSECFilings() {
  const filings = baseData.filings || [];
  if (!filings.length) {
    $('#secFilings').innerHTML = `<div class="card-title">SEC Filings</div><p class="text-slate-500 text-sm">No filings found.</p>`;
    return;
  }
  const rows = filings.map(f => `<tr>
    <td><span class="badge badge-blue">${esc(f.filing_type)}</span></td>
    <td>${esc(f.date)}</td>
    <td>${esc(f.description)}</td>
    <td><a href="${esc(f.url)}" target="_blank" rel="noopener" class="text-blue-400 hover:underline text-xs">View &rarr;</a></td>
  </tr>`).join('');
  $('#secFilings').innerHTML = `
    <div class="card-title">SEC Filings</div>
    <div class="table-scroll"><table class="data-table">
      <thead><tr><th>Type</th><th>Date</th><th>Description</th><th>Link</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>`;
}

// ─── Render: Finviz ─────────────────────────────────────────────────────────

function renderFinviz() {
  if (!finvizData) return;
  renderKeyMetrics();       // augment with RSI/Recom
  renderAnalystConsensus(); // augment with Finviz rec
  renderShortInterest();
  renderAnalystRatings();
  renderAllFinviz();
  renderUnifiedNews();
}

function renderShortInterest() {
  const m = finvizData?.metrics || {};
  const items = [
    ['Short Float',     m['Short Float']  || '—'],
    ['Short Ratio',     m['Short Ratio']  || '—'],
    ['Insider Own',     m['Insider Own']  || '—'],
    ['Insider Trans',   m['Insider Trans']|| '—'],
    ['Inst. Own',       m['Inst Own']     || '—'],
    ['Inst. Trans',     m['Inst Trans']   || '—'],
    ['Float',           m['Shs Float']    || '—'],
    ['Shares Out.',     m['Shs Outstand'] || '—'],
    ['Rel. Volume',     m['Rel Volume']   || '—'],
    ['Volatility',      m['Volatility']   || '—'],
    ['SMA 20',          m['SMA20']        || '—'],
    ['SMA 200',         m['SMA200']       || '—'],
  ];
  $('#shortInterest').innerHTML = `
    <div class="card-title">Short Interest &amp; Ownership</div>
    <div class="metric-grid">${items.map(([l,v]) =>
      `<div class="metric-item"><div class="metric-label">${esc(l)}</div><div class="metric-value">${esc(v)}</div></div>`
    ).join('')}</div>`;
}

function renderAnalystRatings() {
  const fvRatings = finvizData?.ratings || [];
  const udYahoo   = yahooAnalysis?.upgrades_downgrades || [];
  const all = [
    ...fvRatings.map(r => ({
      date: r.date, action: r.action, firm: r.firm,
      rating: r.rating, price_target: r.price_target,
    })),
    ...udYahoo.map(r => ({
      date: r.date, action: r.action, firm: r.firm,
      rating: r.details || '', price_target: '',
    })),
  ];

  if (!all.length) {
    $('#analystRatings').innerHTML = `<div class="card-title">Analyst Ratings &amp; Upgrades</div><p class="text-slate-500 text-sm">No recent analyst activity.</p>`;
    return;
  }
  const rows = all.slice(0,30).map(r => `<tr>
    <td class="whitespace-nowrap text-slate-400">${esc(r.date)}</td>
    <td><span class="badge ${actionClass(r.action)}">${esc(r.action)}</span></td>
    <td class="font-medium">${esc(r.firm)}</td>
    <td class="text-slate-300">${esc(r.rating)}</td>
    <td class="font-mono text-slate-300">${esc(r.price_target)}</td>
  </tr>`).join('');
  $('#analystRatings').innerHTML = `
    <div class="card-title">Analyst Ratings &amp; Upgrades / Downgrades</div>
    <div class="table-scroll"><table class="data-table">
      <thead><tr><th>Date</th><th>Action</th><th>Firm</th><th>Rating</th><th>PT</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>`;
}

function renderAllFinviz() {
  const m = finvizData?.metrics || {};
  const keys = Object.keys(m);
  if (!keys.length) { $('#allFinviz').innerHTML = '<div class="card-title">Finviz Metrics</div><p class="text-slate-500 text-sm">No data.</p>'; return; }
  $('#allFinviz').innerHTML = `
    <div class="card-title">Full Finviz Snapshot</div>
    <div class="metric-grid">${keys.map(k =>
      `<div class="metric-item"><div class="metric-label">${esc(k)}</div><div class="metric-value">${esc(m[k])}</div></div>`
    ).join('')}</div>`;
}

// ─── Render: Yahoo Analysis ─────────────────────────────────────────────────

function renderYahoo() {
  renderAnalystRatings();
  renderEarningsEstimates();
}

function renderEarningsEstimates() {
  const tables = yahooAnalysis?.tables || [];
  if (!tables.length) {
    $('#earningsEstimates').innerHTML = `<div class="card-title">Earnings &amp; Revenue Estimates</div><p class="text-slate-500 text-sm">No data available.</p>`;
    return;
  }
  let html = '<div class="card-title">Earnings &amp; Revenue Estimates</div>';
  tables.forEach(t => {
    html += `<h3 class="text-sm font-semibold text-slate-300 mt-4 mb-2">${esc(t.heading)}</h3>`;
    if (t.headers.length && t.rows.length) {
      html += '<div class="table-scroll"><table class="data-table"><thead><tr>';
      t.headers.forEach(h => { html += `<th>${esc(h)}</th>`; });
      html += '</tr></thead><tbody>';
      t.rows.forEach(row => { html += '<tr>' + row.map(c => `<td>${esc(c)}</td>`).join('') + '</tr>'; });
      html += '</tbody></table></div>';
    }
  });
  $('#earningsEstimates').innerHTML = html;
}

// ─── Render: Insider Trading ────────────────────────────────────────────────

function renderInsider() {
  if (!insiderData) return;
  const txns = insiderData.transactions || [];
  const sum  = insiderData.summary || {};
  const sentCls = sum.net_sentiment === 'Bullish' ? 'badge-green'
               : sum.net_sentiment === 'Bearish' ? 'badge-red' : 'badge-yellow';
  let summaryHtml = '';
  if (sum.total_buys != null || sum.total_sells != null) {
    summaryHtml = `<div class="flex flex-wrap gap-3 mb-4">
      <span class="badge ${sentCls}">${esc(sum.net_sentiment)}</span>
      <div class="metric-item"><div class="metric-label">Buys</div><div class="metric-value clr-green">${sum.total_buys}</div></div>
      <div class="metric-item"><div class="metric-label">Sells</div><div class="metric-value clr-red">${sum.total_sells}</div></div>
      <div class="metric-item"><div class="metric-label">Buy Value</div><div class="metric-value clr-green">$${fmtLarge(sum.total_buy_value)}</div></div>
      <div class="metric-item"><div class="metric-label">Sell Value</div><div class="metric-value clr-red">$${fmtLarge(sum.total_sell_value)}</div></div>
    </div>`;
  }
  let tableHtml = '<p class="text-slate-500 text-sm">No insider transactions found.</p>';
  if (txns.length) {
    tableHtml = `<div class="table-scroll"><table class="data-table">
      <thead><tr><th>Date</th><th>Insider</th><th>Title</th><th>Type</th><th>Price</th><th>Qty</th><th>Value</th></tr></thead>
      <tbody>${txns.slice(0,20).map(t => {
        const isBuy = t.trade_type.includes('Purchase') || t.trade_type.includes('Buy');
        return `<tr>
          <td class="whitespace-nowrap text-slate-400">${esc(t.trade_date)}</td>
          <td class="font-medium">${esc(t.insider_name)}</td>
          <td class="text-xs text-slate-400">${esc(t.title)}</td>
          <td class="${isBuy?'clr-green':'clr-red'}">${esc(t.trade_type)}</td>
          <td class="font-mono">${esc(t.price)}</td>
          <td class="font-mono">${esc(t.qty)}</td>
          <td class="font-mono">${esc(t.value)}</td>
        </tr>`;
      }).join('')}</tbody>
    </table></div>`;
  }
  $('#insiderTrading').innerHTML = `<div class="card-title">Insider Trading</div>${summaryHtml}${tableHtml}`;
}

// ─── Render: Portfolio 123 ──────────────────────────────────────────────────

function renderP123() {
  if (!p123Data) return;

  if (p123Data.error) {
    const msgs = {
      not_configured: 'Set P123_API_ID and P123_API_KEY in your .env file to enable Portfolio 123 data.',
      invalid_credentials: 'Portfolio 123 credentials are invalid. Check P123_API_ID / P123_API_KEY.',
      timeout: 'Portfolio 123 request timed out.',
      no_data: `${p123Data.note || 'No P123 data returned for this ticker.'}`,
    };
    const msg = msgs[p123Data.error] || `Portfolio 123 error: ${p123Data.error}`;
    $('#p123Section').innerHTML = `
      <div class="card-title">Portfolio 123</div>
      <p class="text-slate-500 text-sm">${esc(msg)}</p>`;
    return;
  }

  const metrics = p123Data.metrics || [];
  if (!metrics.length) {
    $('#p123Section').innerHTML = `<div class="card-title">Portfolio 123</div><p class="text-slate-500 text-sm">No data returned.</p>`;
    return;
  }

  // Split into groups for display
  const valuation = ['P/E Ratio','Price / Book','Price / Sales','EV / EBITDA'];
  const quality   = ['Piotroski F-Score','Altman Z-Score','Return on Equity','Return on Assets',
                     'Gross Margin','Operating Margin','Net Margin'];
  const growth    = ['Revenue Growth (YoY)','EPS Growth (YoY)'];
  const other     = ['Debt / Equity','Current Ratio','Beta (252d)','% from 52W High',
                     'Days to Earnings','Avg Vol (20d)','Price'];

  function metricsGrid(labels) {
    return metrics.filter(m => labels.includes(m.label)).map(m => {
      let valHtml = fmtP123(m.value, m.format);
      // Special Piotroski colouring
      if (m.label === 'Piotroski F-Score' && m.value != null) {
        const v = Number(m.value);
        const cls = v >= 7 ? 'piotroski-high' : v >= 4 ? 'piotroski-mid' : 'piotroski-low';
        valHtml = `<span class="${cls}">${valHtml} <span class="text-xs">/9</span></span>`;
      }
      return `<div class="metric-item"><div class="metric-label">${esc(m.label)}</div><div class="metric-value">${valHtml}</div></div>`;
    }).join('');
  }

  $('#p123Section').innerHTML = `
    <div class="card-title">Portfolio 123 <span class="text-slate-600 font-normal normal-case tracking-normal text-xs ml-2">Factor Data</span></div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
      <div>
        <div class="text-xs text-slate-500 uppercase tracking-wide mb-2">Valuation</div>
        <div class="metric-grid">${metricsGrid(valuation)}</div>
      </div>
      <div>
        <div class="text-xs text-slate-500 uppercase tracking-wide mb-2">Quality</div>
        <div class="metric-grid">${metricsGrid(quality)}</div>
      </div>
      <div>
        <div class="text-xs text-slate-500 uppercase tracking-wide mb-2">Growth</div>
        <div class="metric-grid">${metricsGrid(growth)}</div>
      </div>
      <div>
        <div class="text-xs text-slate-500 uppercase tracking-wide mb-2">Other</div>
        <div class="metric-grid">${metricsGrid(other)}</div>
      </div>
    </div>`;
}

// ─── Render: Unified News Feed ──────────────────────────────────────────────

function renderUnifiedNews() {
  // Merge from all available news sources
  const apiArticles  = newsApis?.articles || [];
  const statuses     = newsApis?.source_statuses || {};
  const deepPremium  = newsDeep?.deep_analysis || [];
  const deepOther    = newsDeep?.articles || [];
  const fvNews       = (finvizData?.news || []).map(n => ({
    source: n.source || 'Finviz', source_id: 'finviz',
    headline: n.title, summary: '', url: n.url, published_at: '', sentiment: null,
    sentiment_score: null, timed_out: false,
  }));
  const baseRss      = (baseData?.news || []).map(n => ({
    source: n.source || 'Yahoo RSS', source_id: 'yahoo',
    headline: n.title, summary: '', url: n.link, published_at: n.published,
    sentiment: null, sentiment_score: null, timed_out: false,
  }));
  const googlePremium = deepPremium.map(a => ({
    source: a.source, source_id: a.tier, headline: a.title, summary: '',
    url: a.url, published_at: '', sentiment: null, sentiment_score: null, timed_out: false,
  }));

  // Deduplicate by URL
  const seen = new Set();
  const all = [];
  [...apiArticles, ...googlePremium, ...fvNews, ...deepOther.map(a => ({
    source: a.source, source_id: a.tier, headline: a.title, summary: '',
    url: a.url, published_at: '', sentiment: null, sentiment_score: null, timed_out: false,
  })), ...baseRss].forEach(a => {
    if (!a.headline || a.timed_out) return;
    const key = (a.url || a.headline).toLowerCase().replace(/\/$/, '');
    if (key && !seen.has(key)) { seen.add(key); all.push(a); }
  });

  // Timeout notices
  const timedOut = (newsApis?.articles || []).filter(a => a.timed_out);

  // Source status indicators (no_key → unconfigured)
  const unconfigured = Object.entries(statuses)
    .filter(([,s]) => s === 'no_key')
    .map(([n]) => n);

  if (!all.length && !timedOut.length) {
    const waiting = !newsApis && !newsDeep ? '<p class="text-slate-500 text-sm">Fetching news…</p>' : '<p class="text-slate-500 text-sm">No articles found.</p>';
    $('#newsSection').innerHTML = `<div class="card-title">News &amp; Articles</div>${waiting}`;
    return;
  }

  // Sort API articles with timestamp first, then rest
  const withDate = all.filter(a => a.published_at);
  const noDate   = all.filter(a => !a.published_at);
  withDate.sort((a,b) => b.published_at.localeCompare(a.published_at));
  const sorted = [...withDate, ...noDate];

  let html = `<div class="flex items-center justify-between mb-3">
    <div class="card-title mb-0">News &amp; Articles <span class="text-slate-600 font-normal normal-case text-xs">${sorted.length} items</span></div>
  </div>`;

  // Source status bar
  if (unconfigured.length || timedOut.length) {
    html += `<div class="flex flex-wrap gap-2 mb-3 text-xs">`;
    if (unconfigured.length) html += `<span class="text-slate-500">Not configured: ${unconfigured.map(esc).join(', ')}</span>`;
    timedOut.forEach(a => { html += `<span class="badge badge-red">&#x23F1; ${esc(a.source)} timed out</span>`; });
    html += `</div>`;
  }

  sorted.forEach(a => {
    const pubStr = a.published_at ? new Date(a.published_at).toLocaleDateString('en-US', {month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}) : '';
    html += `<a href="${esc(a.url)}" target="_blank" rel="noopener" class="article-item">
      <div class="flex items-start gap-2">
        <div class="timeline-dot bg-slate-600 mt-1"></div>
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap items-center gap-1.5 mb-0.5">
            ${sourceBadge(a.source_id, a.source)}
            ${a.sentiment ? sentimentBadge(a.sentiment, a.sentiment_score) : ''}
            ${pubStr ? `<span class="text-xs text-slate-500">${esc(pubStr)}</span>` : ''}
          </div>
          <div class="text-sm text-slate-200">${esc(a.headline)}</div>
          ${a.summary ? `<div class="text-xs text-slate-500 mt-0.5 line-clamp-2">${esc(a.summary)}</div>` : ''}
        </div>
      </div>
    </a>`;
  });

  $('#newsSection').innerHTML = html;
}
