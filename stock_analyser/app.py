"""
Portfolio Analysis — Streamlit app
Run with: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date, timedelta
from analysis import run_analysis, BENCHMARK

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Portfolio Analyser",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Portfolio Analyser")
st.caption("Select your holdings, set weights, pick a date range, and hit Analyse.")

# ── Ticker catalogue ──────────────────────────────────────────────────────────

CATALOGUE = {
    # ── Mega-cap stocks ────────────────────────────────────────────────────────
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "NVDA":  "NVIDIA",
    "GOOGL": "Alphabet (A)",
    "GOOG":  "Alphabet (C)",
    "AMZN":  "Amazon",
    "META":  "Meta",
    "TSLA":  "Tesla",
    "BRK-B": "Berkshire Hathaway",
    "LLY":   "Eli Lilly",
    "V":     "Visa",
    "JPM":   "JPMorgan Chase",
    "UNH":   "UnitedHealth",
    "XOM":   "Exxon Mobil",
    "MA":    "Mastercard",
    "JNJ":   "Johnson & Johnson",
    "AVGO":  "Broadcom",
    "HD":    "Home Depot",
    "PG":    "Procter & Gamble",
    "MRK":   "Merck",
    "COST":  "Costco",
    "ABBV":  "AbbVie",
    "CVX":   "Chevron",
    "CRM":   "Salesforce",
    "BAC":   "Bank of America",
    "NFLX":  "Netflix",
    "AMD":   "AMD",
    "KO":    "Coca-Cola",
    "PEP":   "PepsiCo",
    "WMT":   "Walmart",
    "TMO":   "Thermo Fisher",
    "ORCL":  "Oracle",
    "MCD":   "McDonald's",
    "CSCO":  "Cisco",
    "ABT":   "Abbott",
    "ACN":   "Accenture",
    "GE":    "GE Aerospace",
    "DHR":   "Danaher",
    "TXN":   "Texas Instruments",
    "NEE":   "NextEra Energy",
    "PM":    "Philip Morris",
    "IBM":   "IBM",
    "RTX":   "RTX Corp",
    "QCOM":  "Qualcomm",
    "AMGN":  "Amgen",
    "NOW":   "ServiceNow",
    "SPGI":  "S&P Global",
    "GS":    "Goldman Sachs",
    "MS":    "Morgan Stanley",
    "BLK":   "BlackRock",
    "AXP":   "American Express",
    "SYK":   "Stryker",
    "ISRG":  "Intuitive Surgical",
    "ADI":   "Analog Devices",
    "GILD":  "Gilead Sciences",
    "MMC":   "Marsh McLennan",
    "PLD":   "Prologis",
    "UBER":  "Uber",
    "SHOP":  "Shopify",
    "SPOT":  "Spotify",
    "COIN":  "Coinbase",
    "PLTR":  "Palantir",
    "ARM":   "Arm Holdings",
    "SMCI":  "Super Micro",
    "SNOW":  "Snowflake",
    "CRWD":  "CrowdStrike",
    "PANW":  "Palo Alto Networks",
    "DDOG":  "Datadog",
    "ZS":    "Zscaler",
    "NET":   "Cloudflare",
    "MU":    "Micron",
    "INTC":  "Intel",
    "AMAT":  "Applied Materials",
    "LRCX":  "Lam Research",
    "KLAC":  "KLA Corp",
    "ASML":  "ASML",
    "TSM":   "TSMC",
    "BABA":  "Alibaba",
    "PDD":   "PDD Holdings",
    "JD":    "JD.com",
    "NVO":   "Novo Nordisk",
    "SAP":   "SAP",
    # ── Broad market ETFs ──────────────────────────────────────────────────────
    "SPY":   "ETF — S&P 500 (SPDR)",
    "VOO":   "ETF — S&P 500 (Vanguard)",
    "IVV":   "ETF — S&P 500 (iShares)",
    "QQQ":   "ETF — Nasdaq-100",
    "QQQM":  "ETF — Nasdaq-100 (mini)",
    "DIA":   "ETF — Dow Jones",
    "IWM":   "ETF — Russell 2000",
    "VTI":   "ETF — Total US Market",
    "VT":    "ETF — Total World",
    "VXUS":  "ETF — Ex-US World",
    "EFA":   "ETF — Developed Markets",
    "EEM":   "ETF — Emerging Markets",
    "VWO":   "ETF — Emerging Markets (Vanguard)",
    # ── Sector ETFs ────────────────────────────────────────────────────────────
    "XLK":   "ETF — Technology",
    "XLF":   "ETF — Financials",
    "XLV":   "ETF — Healthcare",
    "XLE":   "ETF — Energy",
    "XLY":   "ETF — Consumer Discretionary",
    "XLP":   "ETF — Consumer Staples",
    "XLI":   "ETF — Industrials",
    "XLU":   "ETF — Utilities",
    "XLRE":  "ETF — Real Estate",
    "XLB":   "ETF — Materials",
    "XLC":   "ETF — Communication",
    "SMH":   "ETF — Semiconductors",
    "SOXX":  "ETF — Semiconductors (iShares)",
    "ARKK":  "ETF — ARK Innovation",
    "ARKG":  "ETF — ARK Genomic",
    # ── Fixed income & alternatives ────────────────────────────────────────────
    "AGG":   "ETF — US Aggregate Bond",
    "BND":   "ETF — Total Bond Market",
    "TLT":   "ETF — 20+ Yr Treasury",
    "IEF":   "ETF — 7-10 Yr Treasury",
    "SHY":   "ETF — 1-3 Yr Treasury",
    "LQD":   "ETF — Investment Grade Corp",
    "HYG":   "ETF — High Yield Corp",
    "TIP":   "ETF — TIPS",
    "GLD":   "ETF — Gold",
    "IAU":   "ETF — Gold (iShares)",
    "SLV":   "ETF — Silver",
    "USO":   "ETF — Oil",
    "UNG":   "ETF — Natural Gas",
    "PDBC":  "ETF — Commodities",
    "VNQ":   "ETF — US REITs",
    # ── Leveraged / inverse ────────────────────────────────────────────────────
    "TQQQ":  "ETF — 3× Nasdaq-100",
    "UPRO":  "ETF — 3× S&P 500",
    "SQQQ":  "ETF — -3× Nasdaq-100",
    "SPXU":  "ETF — -3× S&P 500",
    # ── Indexes (benchmark / reference only) ───────────────────────────────────
    "^GSPC": "Index — S&P 500",
    "^IXIC": "Index — Nasdaq Composite",
    "^DJI":  "Index — Dow Jones",
    "^RUT":  "Index — Russell 2000",
    "^VIX":  "Index — CBOE Volatility",
    "^TNX":  "Index — 10-Yr Treasury Yield",
}

# Build the option labels shown in the dropdown: "AAPL — Apple"
OPTION_LABELS  = {f"{t} — {n}": t for t, n in CATALOGUE.items()}
DEFAULT_LABELS = [lbl for lbl, t in OPTION_LABELS.items()
                  if t in ("AAPL", "MSFT", "GOOGL", "AMZN", "NVDA")]

# ── Sidebar — inputs ──────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Portfolio")

    selected_labels = st.multiselect(
        "Search and select holdings",
        options=list(OPTION_LABELS.keys()),
        default=DEFAULT_LABELS,
        placeholder="Type to search…",
    )
    tickers = [OPTION_LABELS[lbl] for lbl in selected_labels]

    raw_weights = []
    if tickers:
        st.caption("Set weights (will be normalised to 100%)")
        equal = round(100 / len(tickers), 1)
        for t in tickers:
            w = st.number_input(
                t, min_value=0.0, max_value=100.0,
                value=equal, step=1.0, key=f"w_{t}",
            )
            raw_weights.append(w)

        total_w = sum(raw_weights)
        st.caption(f"Total: **{total_w:.1f}%** {'✅' if abs(total_w - 100) < 0.5 else '→ will be normalised'}")

    st.divider()
    st.subheader("Date range")
    end_default   = date.today()
    start_default = end_default - timedelta(days=3 * 365)
    start_date = st.date_input("From", value=start_default)
    end_date   = st.date_input("To",   value=end_default)

    st.divider()
    st.subheader("Settings")
    risk_free = st.slider("Risk-free rate (%)", 0.0, 10.0, 5.25, 0.25) / 100

    run = st.button("🔍 Analyse", use_container_width=True, type="primary")

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_pct(v: float) -> str:
    return f"{v:.2%}"

def fmt_num(v: float, decimals: int = 3) -> str:
    return f"{v:.{decimals}f}"

METRIC_FMT = {
    "Annualised Return":     (fmt_pct,  "delta"),
    "Annualised Volatility": (fmt_pct,  "plain"),
    "Sharpe Ratio":          (lambda v: fmt_num(v, 3), "plain"),
    "Max Drawdown":          (fmt_pct,  "delta"),
    "VaR (95%, 1-day)":     (fmt_pct,  "plain"),
    "Beta (vs SPY)":         (lambda v: fmt_num(v, 3), "plain"),
}

COLORS = px.colors.qualitative.Plotly

# ── Run ───────────────────────────────────────────────────────────────────────

if run:
    if len(tickers) == 0:
        st.error("Enter at least one ticker.")
        st.stop()
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    with st.spinner("Fetching data and computing metrics…"):
        try:
            data = run_analysis(
                tickers=tickers,
                weights=raw_weights,
                start=str(start_date),
                end=str(end_date),
                risk_free=risk_free,
            )
        except ValueError as e:
            st.error(str(e))
            st.stop()

    st.session_state["data"] = data


data = st.session_state.get("data")

if data is None:
    st.info("Configure your portfolio in the sidebar and click **Analyse**.")
else:
    tickers  = data["tickers"]
    weights  = data["weights"]
    metrics  = data["metrics"]
    cum      = data["cum_returns"]
    dd       = data["dd_series"]
    returns  = data["returns"]
    port_ret = data["port_ret"]

    # ── Metrics cards ─────────────────────────────────────────────────────────

    st.subheader("Portfolio Metrics")
    cols = st.columns(len(metrics))
    for col, (name, value) in zip(cols, metrics.items()):
        fmt_fn, style = METRIC_FMT[name]
        delta = fmt_fn(value) if style == "delta" else None
        col.metric(label=name, value=fmt_fn(value), delta=delta)

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Cumulative Returns",
        "📉 Drawdown",
        "🔥 Correlation",
        "⚖️ Risk vs Return",
        "📐 Return Distribution",
    ])

    # ── Tab 1: Cumulative returns ──────────────────────────────────────────────

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum[BENCHMARK],
            name=BENCHMARK, line=dict(color="orange", dash="dash", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum["Portfolio"],
            name="Portfolio", line=dict(color="steelblue", width=3),
        ))
        for i, t in enumerate(tickers):
            fig.add_trace(go.Scatter(
                x=cum.index, y=cum[t],
                name=t, line=dict(color=COLORS[i % len(COLORS)], width=1.5),
                visible="legendonly",
            ))
        fig.update_layout(
            title="Cumulative Return (%)",
            yaxis_title="Return (%)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=480,
        )
        fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Individual stocks are hidden by default — click their names in the legend to show them.")

    # ── Tab 2: Drawdown ────────────────────────────────────────────────────────

    with tab2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dd.index, y=dd,
            fill="tozeroy",
            name="Drawdown",
            line=dict(color="crimson", width=1),
            fillcolor="rgba(220,20,60,0.3)",
        ))
        fig.update_layout(
            title="Portfolio Drawdown (%)",
            yaxis_title="Drawdown (%)",
            hovermode="x unified",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Maximum Drawdown", fmt_pct(metrics["Max Drawdown"]))

    # ── Tab 3: Correlation heatmap ─────────────────────────────────────────────

    with tab3:
        corr = returns[tickers].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        corr_masked = corr.where(~mask)
        fig = px.imshow(
            corr_masked,
            text_auto=".2f",
            color_continuous_scale="RdYlGn",
            zmin=-1, zmax=1,
            title="Return Correlation Matrix",
            aspect="auto",
        )
        fig.update_layout(height=max(400, len(tickers) * 70))
        st.plotly_chart(fig, use_container_width=True)

    # ── Tab 4: Risk vs Return ──────────────────────────────────────────────────

    with tab4:
        from analysis import annualised_return, annualised_volatility

        rows = []
        for i, t in enumerate(tickers):
            rows.append({
                "Ticker": t,
                "Return (%)":     annualised_return(returns[t]) * 100,
                "Volatility (%)": annualised_volatility(returns[t]) * 100,
                "Type": "Stock",
            })
        rows.append({
            "Ticker": "Portfolio ★",
            "Return (%)":     annualised_return(port_ret) * 100,
            "Volatility (%)": annualised_volatility(port_ret) * 100,
            "Type": "Portfolio",
        })
        rows.append({
            "Ticker": BENCHMARK,
            "Return (%)":     annualised_return(data["bench_ret"]) * 100,
            "Volatility (%)": annualised_volatility(data["bench_ret"]) * 100,
            "Type": "Benchmark",
        })
        df_rv = pd.DataFrame(rows)
        color_map  = {"Stock": "steelblue", "Portfolio": "gold", "Benchmark": "darkorange"}
        symbol_map = {"Stock": "circle",    "Portfolio": "star", "Benchmark": "diamond"}
        fig = px.scatter(
            df_rv, x="Volatility (%)", y="Return (%)", text="Ticker",
            color="Type", symbol="Type",
            color_discrete_map=color_map,
            symbol_map=symbol_map,
            title="Annualised Risk vs Return",
            height=500,
        )
        fig.update_traces(textposition="top center", marker=dict(size=14))
        fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            df_rv.drop(columns="Type").set_index("Ticker").style.format("{:.2f}"),
            use_container_width=True,
        )

    # ── Tab 5: Return distribution ─────────────────────────────────────────────

    with tab5:
        from scipy.stats import norm as scipy_norm
        from analysis import value_at_risk

        daily_pct = port_ret * 100
        mu, sigma = daily_pct.mean(), daily_pct.std()
        var95 = value_at_risk(port_ret) * 100

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=daily_pct, nbinsx=80,
            histnorm="probability density",
            name="Daily Returns",
            marker_color="steelblue",
            opacity=0.7,
        ))
        x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 400)
        fig.add_trace(go.Scatter(
            x=x, y=scipy_norm.pdf(x, mu, sigma),
            name="Normal fit",
            line=dict(color="red", width=2),
        ))
        fig.add_vline(x=var95, line_dash="dash", line_color="orange",
                      annotation_text=f"VaR 95%: {var95:.2f}%",
                      annotation_position="top right")
        fig.update_layout(
            title="Portfolio Daily Return Distribution",
            xaxis_title="Daily Return (%)",
            yaxis_title="Density",
            hovermode="x unified",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Mean daily return", f"{mu:.3f}%")
        col2.metric("Daily std dev",     f"{sigma:.3f}%")
        col3.metric("Skewness",          f"{daily_pct.skew():.3f}")

    # ── Holdings table ─────────────────────────────────────────────────────────

    st.divider()
    st.subheader("Holdings")

    total_w = sum(weights)
    sm = data["stock_metrics"]
    rows = []
    for t, w in zip(tickers, weights):
        m = sm[t]
        rows.append({
            "Ticker":        t,
            "Weight":        f"{w / total_w:.1%}",
            "Ann. Return":   f"{m['Annualised Return']:.2%}",
            "Volatility":    f"{m['Annualised Volatility']:.2%}",
            "Sharpe":        f"{m['Sharpe Ratio']:.3f}",
            "Max Drawdown":  f"{m['Max Drawdown']:.2%}",
        })
    st.dataframe(pd.DataFrame(rows).set_index("Ticker"), use_container_width=True)
