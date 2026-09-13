import os
import time
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

APP_VERSION = "V8.9-STOCKS-RIDES+EARLY-WATCH-V4+ENTRY-RESEARCH-V3"
API_URL = os.getenv("FLOWRIDE_API_URL", "").rstrip("/")
API_KEY = os.getenv("FLOWRIDE_API_KEY", "")
PAYMENT_URL = os.getenv("PAYMENT_URL", "")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "")
try:
    API_URL = st.secrets.get("FLOWRIDE_API_URL", API_URL).rstrip("/")
    API_KEY = st.secrets.get("FLOWRIDE_API_KEY", API_KEY)
    PAYMENT_URL = st.secrets.get("PAYMENT_URL", PAYMENT_URL)
    SUPPORT_EMAIL = st.secrets.get("SUPPORT_EMAIL", SUPPORT_EMAIL)
except Exception:
    pass

st.set_page_config(page_title="Stocks Rides PRO", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1200px;}
.hero {padding: 8px 0 12px 0;}
.hero-title {font-size: 2.2rem; font-weight: 850; line-height: 1.1; margin: 0;}
.hero-sub {font-size: 1.05rem; margin-top: .35rem; opacity: .78;}
.status {padding: .8rem 1rem; border-radius: 12px; background: rgba(35,116,190,.16); border: 1px solid rgba(35,116,190,.35); margin-bottom: 1rem;}
.flow-card {padding: 18px; border-radius: 16px; text-align:center; margin: 10px 0 18px 0;}
.flow-buy {background:#dff6e7; color:#126b36; border:1px solid #8dd5a6;}
.flow-ride {background:#e3efff; color:#1559a6; border:1px solid #8db7ef;}
.flow-exit {background:#ffe3e3; color:#a51f1f; border:1px solid #ef9a9a;}
.flow-state {font-size: 32px; font-weight: 850;}
.flow-score {font-size: 15px; font-weight: 650; margin-top: 5px;}
.small-note {font-size: .9rem; opacity: .72;}
@media (max-width: 600px) { .hero-title {font-size: 1.85rem;} .flow-state {font-size: 27px;} }
</style>
""", unsafe_allow_html=True)

# Native Streamlit header — deliberately avoids custom HTML so it cannot be clipped/hidden by theme CSS.
st.title("🇮🇳 Stocks Rides")
st.markdown("### **PRO • STOCKS RIDES**")
st.caption("Find the trend. Ride the flow. Exit when the flow breaks.")
st.markdown("🟢 **BUY**  →  🔵 **RIDE**  →  🔴 **EXIT**")

if not API_URL or not API_KEY:
    st.error("Backend configuration is missing. Set FLOWRIDE_API_URL and FLOWRIDE_API_KEY in Streamlit Secrets.")
    st.stop()

def call(path, params=None, timeout=90):
    """Call the protected FLOWRIDE API without exposing the API key."""
    try:
        r = requests.get(
            API_URL + path,
            params=params or {},
            headers={"X-API-Key": API_KEY, "Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach backend: {e}") from e

    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        if r.status_code in (401, 403):
            raise RuntimeError("API authentication failed. Check FLOWRIDE_API_KEY in Streamlit Secrets.")
        raise RuntimeError(str(detail))

    try:
        return r.json()
    except ValueError as e:
        raise RuntimeError("Backend returned an invalid JSON response.") from e


def call_post(path, params=None, timeout=60):
    """POST to the protected FLOWRIDE API without exposing the API key."""
    try:
        r = requests.post(
            API_URL + path,
            params=params or {},
            headers={"X-API-Key": API_KEY, "Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach backend: {e}") from e

    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        if r.status_code in (401, 403):
            raise RuntimeError("API authentication failed. Check FLOWRIDE_API_KEY in Streamlit Secrets.")
        raise RuntimeError(str(detail))

    try:
        return r.json()
    except ValueError as e:
        raise RuntimeError("Backend returned an invalid JSON response.") from e


def call_bytes(path, params=None, timeout=120):
    """Download protected non-JSON content (for example Signal Research CSV)."""
    try:
        r = requests.get(
            API_URL + path,
            params=params or {},
            headers={"X-API-Key": API_KEY, "Accept": "text/csv"},
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise RuntimeError(f"Could not reach backend: {e}") from e
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(str(detail))
    return r.content

try:
    h = requests.get(API_URL + "/health", timeout=20).json()
    st.markdown(f'<div class="status">Backend: <b>ONLINE</b> • {h.get("version", "unknown")}<br>Universe: <b>{h.get("total", 0):,}</b> securities • NSE <b>{h.get("nse", 0):,}</b> • BSE <b>{h.get("bse", 0):,}</b></div>', unsafe_allow_html=True)
except Exception as e:
    st.warning("Backend is waking up or unavailable. Try again in a moment.")

with st.sidebar:
    st.markdown("## STOCKS RIDES PRO")
    st.caption("Simple ride signals. Advanced analysis stays on the private server.")
    st.markdown("🟢 **BUY**  →  🔵 **RIDE**  →  🔴 **EXIT**")
    st.divider()
    st.markdown("### PRO plans")
    st.markdown("**₹499/month**\n\nFull scanner • FLOWRIDE • Historical signals")
    st.markdown("**₹2,999/year**\n\nBest value • Product updates")
    if PAYMENT_URL:
        st.link_button("⭐ Upgrade to PRO", PAYMENT_URL, use_container_width=True)
    if SUPPORT_EMAIL:
        st.caption(f"Support: {SUPPORT_EMAIL}")

st.subheader("🔎 Search Stock")
q = st.text_input("Search NSE/BSE symbol, company name or scrip code", placeholder="RELIANCE, TCS, PRICOL, 500325...", key="search_q")
ex = st.selectbox("Exchange", ["ALL", "NSE", "BSE"], key="search_exchange")
if st.button("🔍 SEARCH", type="primary", use_container_width=True):
    if not q.strip():
        st.warning("Enter a stock symbol, company name or scrip code.")
    else:
        try:
            raw = call("/search", {"q": q.strip(), "exchange": ex})
            results = raw.get("results", raw) if isinstance(raw, dict) else raw
            if not isinstance(results, list):
                raise RuntimeError("Unexpected search response from backend")
            st.session_state.search_results = results
            st.session_state.pop("analysis", None)
            st.session_state.pop("scan", None)
        except Exception as e:
            st.error(f"Search failed: {e}")

results = st.session_state.get("search_results", [])
if results:
    st.success(f"Found {len(results)} matching securities.")
    labels = [f"{x['symbol']} — {x['name']} ({x['exchange']})" for x in results]
    idx = st.selectbox("Select stock", range(len(labels)), format_func=lambda i: labels[i], key="selected_stock")
    selected = results[int(idx)]
    if st.button("📊 ANALYZE SELECTED STOCK", type="primary", use_container_width=True):
        try:
            with st.spinner(f"Analyzing {selected['symbol']}..."):
                st.session_state.analysis = call("/analyze", {"exchange": selected["exchange"], "symbol": selected["symbol"]}, timeout=120)
        except Exception as e:
            st.error(f"Analysis failed: {e}")

analysis = st.session_state.get("analysis")
if analysis:
    m = analysis.get("metrics", {})
    f = analysis.get("flowride", {})
    st.divider()
    st.subheader(f"📊 {analysis.get('name','')} | {analysis.get('symbol','')} ({analysis.get('exchange','')})")
    st.caption(f"Data ticker: `{analysis.get('ticker','—')}` • Latest data: {analysis.get('latest_date','—')} • Source: {analysis.get('data_source_exchange', analysis.get('exchange','—'))}")
    state = str(f.get("state", "RIDE")).upper()
    state_label = "🟢 BUY" if state == "BUY" else "🔵 RIDE" if state == "RIDE" else "🔴 EXIT" if state == "EXIT" else "⚪ FLAT"
    cls = "flow-buy" if state == "BUY" else "flow-exit" if state == "EXIT" else "flow-ride"
    st.caption("CURRENT STOCK RIDE STATE")
    st.markdown(f'<div class="flow-card {cls}"><div class="flow-state">{state_label}</div><div class="flow-score">FLOWRIDE Flow Score {float(f.get("score",0) or 0):.0f}/100</div></div>', unsafe_allow_html=True)

    a,b,c,d,e = st.columns(5)
    a.metric("Close", f"₹{float(m.get('price',0)):,.2f}")
    b.metric("Score", f"{float(m.get('score',0)):.0f}/100")
    c.metric("Signal", str(m.get("signal", "—")))
    d.metric("RSI", f"{float(m['rsi']):.1f}" if m.get("rsi") is not None else "—")
    e.metric("FLOWRIDE", state_label)
    st.markdown("### 🎯 Current Decision")
    decision_text = f"**{f.get('primary_action', '—')}** • {f.get('lifecycle', state)}"
    if state == "BUY":
        st.success(decision_text)
    elif state == "EXIT":
        st.error(decision_text)
    else:
        st.info(decision_text)

    a,b,c = st.columns(3)
    a.metric("Flow Score", f"{float(f.get('score',0) or 0):.0f}/100")
    b.metric("Trailing Flow Stop", f"₹{float(f.get('trail',0) or 0):,.2f}")
    c.metric("Entry Quality", str(f.get("entry_quality", "—")))

    st.markdown("### 🧠 Why this signal?")

    # Keep the explanation aligned with the CURRENT FLOWRIDE state.
    # EXIT must not display bullish/supportive factors beside its exit reasons.
    why = f.get("why", []) or []
    cautions = f.get("cautions", []) or []
    exit_reasons = f.get("exit_reason", []) or []

    if state == "EXIT":
        if exit_reasons:
            st.error("**Exit explanation:** " + " • ".join(exit_reasons))
        else:
            st.warning("**Exit explanation:** The FLOWRIDE engine confirmed EXIT, but no detailed exit reason was returned.")

        # IMPORTANT: Do not display the generic backend `cautions` list during EXIT.
        # The backend list can contain healthy/bullish observations such as
        # "RSI in healthy momentum zone", "Directional strength positive", or
        # "Volume confirmation present". Showing those as cautions beside an EXIT
        # reason is confusing and can contradict the current signal.
        #
        # For EXIT, the UI therefore shows only the authoritative exit_reason.
        # Generic cautions remain visible for BUY/RIDE states below.

    else:
        # BUY and RIDE can show the current supportive and cautionary conditions.
        if why:
            st.markdown("  \n".join([f"✅ {x}" for x in why]))
        if cautions:
            st.markdown("  \n".join([f"⚠️ {x}" for x in cautions[:3]]))

        if not why and not cautions:
            st.info("No additional explanation was returned for the current FLOWRIDE state.")

    st.markdown("### 🛡 FLOW RISK")
    a,b,c = st.columns(3)
    a.metric("Current Price", f"₹{float(m.get('price',0) or 0):,.2f}")
    b.metric("Distance to Flow Stop", f"{float(f.get('risk_distance_pct',0) or 0):.1f}%" if f.get("risk_distance_pct") is not None else "—")
    c.metric("Risk Status", str(f.get("risk_status", "—")))

    rs = f.get("ride_stats", {}) or {}
    if rs.get("entry_price") is not None:
        st.markdown("### 📈 Ride Performance")
        a,b,c,d = st.columns(4)
        a.metric("BUY START", rs.get("entry_date") or "—")
        b.metric("Entry", f"₹{float(rs.get('entry_price') or 0):,.2f}")
        ret = rs.get("return_pct")
        c.metric("Return", f"{float(ret):+.1f}%" if ret is not None else "—")
        d.metric("Ride Days", str(rs.get("duration_days")) if rs.get("duration_days") is not None else "—")
        a,b = st.columns(2)
        mg = rs.get("max_gain_pct"); md = rs.get("max_drawdown_pct")
        a.metric("Maximum Gain", f"{float(mg):+.1f}%" if mg is not None else "—")
        b.metric("Maximum Drawdown", f"{float(md):+.1f}%" if md is not None else "—")

    chart = analysis.get("chart", {})
    dates = chart.get("date", [])
    if dates:
        st.markdown("### 🌊 Stocks Rides — RIDE FLOW HISTORY")
        st.caption("The badge above is the CURRENT state. The blue RIDE FLOW appears only while a confirmed ride is active. 🟢 BUY START begins a ride; 🔴 EXIT ends it. Historical markers are not the current signal.")
        flow_days = st.slider("FLOWRIDE chart period (days)", 60, min(500, len(dates)), min(180, len(dates)), 10, key="flow_chart_days")
        start = max(0, len(dates)-flow_days)
        fd = pd.DataFrame({
            "Date": pd.to_datetime(dates[start:]),
            "Price": chart.get("price", [None]*len(dates))[start:],
            "Flow": chart.get("flow_line", chart.get("ride", [None]*len(dates)))[start:],
            "BUY": chart.get("buy", [None]*len(dates))[start:],
            "EXIT": chart.get("exit", [None]*len(dates))[start:],
        }).set_index("Date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fd.index, y=fd.Price, mode="lines", name="Price", line=dict(width=1.5)))
        fig.add_trace(go.Scatter(x=fd.index, y=fd.Flow, mode="lines", name="ACTIVE RIDE FLOW", connectgaps=False, line=dict(width=4)))
        bx = fd.index[fd.BUY.notna()]; by = fd.loc[bx, "BUY"]
        exx = fd.index[fd.EXIT.notna()]; ey = fd.loc[exx, "EXIT"]
        if len(bx): fig.add_trace(go.Scatter(x=bx, y=by, mode="markers+text", name="BUY START", marker=dict(size=13, symbol="triangle-up"), text=["BUY START"]*len(bx), textposition="top center"))
        if len(exx): fig.add_trace(go.Scatter(x=exx, y=ey, mode="markers+text", name="EXIT", marker=dict(size=13, symbol="triangle-down"), text=["EXIT"]*len(exx), textposition="bottom center"))
        fig.update_layout(height=500, hovermode="x unified", xaxis_rangeslider_visible=False, yaxis_title="Price (₹)", legend=dict(orientation="h"), margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### 📈 Technical Dashboard")
        days = st.slider("Technical chart period (days)", 60, min(500, len(dates)), min(180, len(dates)), 10, key="tech_chart_days")
        start = max(0, len(dates)-days)
        d = pd.DataFrame({
            "Date": pd.to_datetime(dates[start:]), "Open": chart.get("open", [None]*len(dates))[start:], "High": chart.get("high", [None]*len(dates))[start:], "Low": chart.get("low", [None]*len(dates))[start:], "Close": chart.get("price", [None]*len(dates))[start:], "Volume": chart.get("volume", [None]*len(dates))[start:], "SMA20": chart.get("sma20", [None]*len(dates))[start:], "SMA50": chart.get("sma50", [None]*len(dates))[start:], "SMA200": chart.get("sma200", [None]*len(dates))[start:], "EMA20": chart.get("ema20", [None]*len(dates))[start:], "EMA50": chart.get("ema50", [None]*len(dates))[start:], "BBUpper": chart.get("bb_upper", [None]*len(dates))[start:], "BBLower": chart.get("bb_lower", [None]*len(dates))[start:], "RSI": chart.get("rsi14", [None]*len(dates))[start:], "MACD": chart.get("macd", [None]*len(dates))[start:], "MACDSignal": chart.get("macd_signal", [None]*len(dates))[start:], "MACDHist": chart.get("macd_hist", [None]*len(dates))[start:]
        }).set_index("Date")
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.52,0.16,0.16,0.16], subplot_titles=("Price / Trend / Bollinger","Volume","RSI (14)","MACD"))
        fig.add_trace(go.Candlestick(x=d.index, open=d.Open, high=d.High, low=d.Low, close=d.Close, name="Candles"), row=1,col=1)
        for col,name in [("SMA20","SMA 20"),("SMA50","SMA 50"),("SMA200","SMA 200"),("EMA20","EMA 20"),("EMA50","EMA 50"),("BBUpper","BB Upper"),("BBLower","BB Lower")]: fig.add_trace(go.Scatter(x=d.index,y=d[col],mode="lines",name=name),row=1,col=1)
        fig.add_trace(go.Bar(x=d.index,y=d.Volume,name="Volume"),row=2,col=1)
        fig.add_trace(go.Scatter(x=d.index,y=d.RSI,mode="lines",name="RSI"),row=3,col=1)
        fig.add_hline(y=70,line_dash="dot",row=3,col=1); fig.add_hline(y=30,line_dash="dot",row=3,col=1)
        fig.add_trace(go.Scatter(x=d.index,y=d.MACD,mode="lines",name="MACD"),row=4,col=1); fig.add_trace(go.Scatter(x=d.index,y=d.MACDSignal,mode="lines",name="Signal"),row=4,col=1); fig.add_trace(go.Bar(x=d.index,y=d.MACDHist,name="Histogram"),row=4,col=1)
        fig.update_layout(height=980,xaxis_rangeslider_visible=False,hovermode="x unified",legend=dict(orientation="h"),margin=dict(l=10,r=10,t=65,b=10))
        fig.update_yaxes(title_text="Price",row=1,col=1); fig.update_yaxes(title_text="Volume",row=2,col=1); fig.update_yaxes(title_text="RSI",range=[0,100],row=3,col=1)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    reasons = m.get("reasons", []) or []
    if reasons: st.info("Positive factors: " + " • ".join(reasons))


st.divider()
st.subheader("📊 FLOWRIDE Historical Backtest")
st.caption("Historical validation uses the same private-server FLOWRIDE BUY → RIDE → EXIT engine as the live analysis. This first version is for strategy validation, not investment advice.")

bt_ex = st.selectbox("Backtest exchange", ["NSE", "BSE"], key="bt_exchange")
bt_symbol = st.text_input(
    "Stock symbol for backtest",
    value=str(selected.get("symbol", "")) if "selected" in globals() and selected else "",
    placeholder="Example: RELIANCE or TCS",
    key="bt_symbol",
).strip().upper()
bt_period = st.selectbox("Backtest period", ["1y", "2y", "5y"], index=1, key="bt_period")
bt_capital = st.number_input(
    "Initial capital (₹)",
    min_value=1000.0,
    max_value=100000000.0,
    value=100000.0,
    step=10000.0,
    key="bt_capital",
)

if st.button("▶ RUN FLOWRIDE BACKTEST", type="primary", use_container_width=True):
    if not bt_symbol:
        st.warning("Enter a stock symbol first.")
    else:
        try:
            with st.spinner(f"Running {bt_period} FLOWRIDE backtest for {bt_symbol}..."):
                st.session_state.flowride_backtest = call(
                    "/backtest",
                    {
                        "exchange": bt_ex,
                        "symbol": bt_symbol,
                        "period": bt_period,
                        "initial_capital": float(bt_capital),
                    },
                    timeout=180,
                )
        except Exception as e:
            st.error(f"Backtest failed: {e}")

bt = st.session_state.get("flowride_backtest")
if bt:
    st.markdown(f"### 📈 {bt.get('name', bt.get('symbol', ''))} — {bt.get('symbol', '')} ({bt.get('period', '')})")
    st.caption(
        f"Data ticker: `{bt.get('ticker', '—')}` • Latest data: {bt.get('latest_date', '—')} "
        f"• Source: {bt.get('data_source_exchange', bt.get('exchange', '—'))}"
    )

    s = bt.get("stats", {}) or {}
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Completed Trades", int(s.get("Completed Trades", 0) or 0))
    c2.metric("Win Rate", f"{float(s.get('Win Rate %', 0) or 0):.1f}%")
    c3.metric("FLOWRIDE Return", f"{float(s.get('Total Return %', 0) or 0):+.1f}%")
    c4.metric("Max Drawdown", f"{float(s.get('Max Drawdown %', 0) or 0):.1f}%")
    c5.metric("Buy & Hold", f"{float(s.get('Buy & Hold Return %', 0) or 0):+.1f}%")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ending Capital", f"₹{float(s.get('Ending Capital', 0) or 0):,.0f}")
    c2.metric("Average Trade", f"{float(s.get('Average Trade %', 0) or 0):+.2f}%")
    c3.metric("Best Trade", f"{float(s.get('Best Trade %', 0) or 0):+.2f}%" if s.get("Best Trade %") is not None else "—")
    c4.metric("Worst Trade", f"{float(s.get('Worst Trade %', 0) or 0):+.2f}%" if s.get("Worst Trade %") is not None else "—")

    eq = pd.DataFrame(bt.get("equity_curve", []) or [])
    if not eq.empty:
        eq["Date"] = pd.to_datetime(eq["Date"])
        eq = eq.sort_values("Date")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=eq["Date"], y=eq["Equity"], mode="lines", name="FLOWRIDE Equity"))
        fig.update_layout(
            title="FLOWRIDE Equity Curve",
            height=420,
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title="Simulated Capital (₹)",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        if "Drawdown %" in eq.columns:
            dd = go.Figure()
            dd.add_trace(go.Scatter(x=eq["Date"], y=eq["Drawdown %"], mode="lines", name="Drawdown"))
            dd.update_layout(
                title="FLOWRIDE Drawdown",
                height=300,
                hovermode="x unified",
                xaxis_title="Date",
                yaxis_title="Drawdown %",
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(dd, use_container_width=True, config={"displayModeBar": False})

    trades = pd.DataFrame(bt.get("trades", []) or [])
    st.markdown("### 🔁 Completed FLOWRIDE Trades")
    if trades.empty:
        st.info("No completed BUY → EXIT cycles were found in this historical window.")
    else:
        st.dataframe(trades, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download Backtest Trades CSV",
            trades.to_csv(index=False).encode("utf-8"),
            file_name=f"flowride_backtest_{bt.get('symbol', 'stock')}_{bt.get('period', 'period')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    open_trade = s.get("Open Trade")
    if open_trade:
        st.markdown("### 🔵 Active Historical Ride")
        st.info(
            f"Entry: ₹{float(open_trade.get('Entry Price', 0) or 0):,.2f} on {open_trade.get('Entry Date', '—')} "
            f"• Current return: {float(open_trade.get('Unrealized Return %', 0) or 0):+.2f}% "
            f"• Holding days: {open_trade.get('Holding Days', '—')}"
        )

    assumptions = bt.get("assumptions", []) or []
    with st.expander("⚙️ Backtest assumptions", expanded=False):
        for item in assumptions:
            st.write(f"• {item}")


st.divider()
st.subheader("🧪 FLOWRIDE Strategy Validation")
st.caption("V8.9 uses representative deterministic sampling. Large validations run in backend batches with live progress, avoiding the old 900-second request timeout.")

ub1, ub2, ub3, ub4, ub5 = st.columns(5)
with ub1:
    ub_exchange = st.selectbox("Exchange", ["NSE", "BSE"], key="ub_exchange")
with ub2:
    ub_limit_choice = st.selectbox(
        "Stocks to test",
        [25, 50, 100, 250, 500, 1000, 2000, 5000, "ALL"],
        index=0,
        key="ub_limit"
    )
    ub_limit = 0 if ub_limit_choice == "ALL" else int(ub_limit_choice)
with ub3:
    ub_period = st.selectbox("Period", ["1y", "2y", "5y"], index=1, key="ub_period")
with ub4:
    ub_capital = st.number_input("Capital per stock (₹)", min_value=1000.0, max_value=100000000.0, value=100000.0, step=10000.0, key="ub_capital")
with ub5:
    ub_seed = st.number_input("Sample seed", min_value=1, max_value=999999, value=89, step=1, key="ub_seed")

if st.button("🧪 RUN STRATEGY VALIDATION", type="primary", use_container_width=True):
    try:
        limit_label = "ALL" if ub_limit == 0 else f"up to {ub_limit}"

        # Start the heavy validation as a background backend job.
        start = call_post(
            "/validation_job/start",
            {
                "exchange": ub_exchange,
                "limit": int(ub_limit),
                "period": ub_period,
                "initial_capital": float(ub_capital),
                "sample_seed": int(ub_seed),
            },
            timeout=60,
        )

        job_id = str(start.get("job_id", "") or "").strip()
        if not job_id:
            raise RuntimeError("Backend did not return a validation job ID.")

        # Safety check: never attach the UI to a background job that was
        # started with different validation settings.
        returned_params = start.get("params", {}) or {}
        expected_params = {
            "exchange": ub_exchange,
            "limit": int(ub_limit),
            "period": ub_period,
            "initial_capital": float(ub_capital),
            "sample_seed": int(ub_seed),
        }
        if returned_params:
            mismatches = {
                k: (expected_params[k], returned_params.get(k))
                for k in expected_params
                if returned_params.get(k) != expected_params[k]
            }
            if mismatches:
                raise RuntimeError(
                    "Backend validation settings do not match the UI selection. "
                    f"Mismatch: {mismatches}. The run was not attached."
                )

        st.session_state.validation_job_id = job_id
        st.session_state.pop("flowride_universe_backtest", None)

        progress = st.progress(0)
        status_box = st.empty()
        status_box.info(
            f"Validation job started • {limit_label} {ub_exchange} stocks • "
            f"{ub_period} • seed {int(ub_seed)}"
        )

        # Poll short status requests instead of holding one 900-second request open.
        # 3,600 seconds permits a slow free/small Render instance while each HTTP
        # request itself stays short and resilient.
        poll_started = time.time()
        max_wait_seconds = 3600
        poll_seconds = 5

        while True:
            status = call(
                "/validation_job/status",
                {"job_id": job_id},
                timeout=30,
            )

            state = str(status.get("status", "") or "").upper()
            pct = float(status.get("percent", 0) or 0)
            processed = status.get("processed")
            total = status.get("total")
            batch = status.get("batch")
            batches = status.get("batches")
            message = status.get("message", state or "Working")

            progress.progress(max(0, min(100, int(round(pct)))))

            parts = [str(message)]
            if processed is not None and total:
                parts.append(f"{int(processed)}/{int(total)} stocks")
            if batch and batches:
                parts.append(f"batch {int(batch)}/{int(batches)}")
            parts.append(f"{pct:.0f}%")
            status_box.info(" • ".join(parts))

            if state == "DONE":
                st.session_state.flowride_universe_backtest = call(
                    "/validation_job/result",
                    {"job_id": job_id},
                    timeout=180,
                )
                progress.progress(100)
                status_box.success("Strategy validation completed.")
                break

            if state == "FAILED":
                raise RuntimeError(status.get("message") or status.get("error") or "Validation job failed.")

            if time.time() - poll_started > max_wait_seconds:
                raise RuntimeError(
                    "Validation is still running after 60 minutes. "
                    f"Job ID: {job_id}. Re-run the page later only after checking backend health."
                )

            time.sleep(poll_seconds)

    except Exception as e:
        st.error(f"Strategy validation failed: {e}")

ub = st.session_state.get("flowride_universe_backtest")
if ub:
    st.markdown(f"### 📊 {ub.get('exchange','NSE')} Validation Results — {ub.get('period','2y')}")
    su = ub.get("summary", {}) or {}

    a,b,c,d,e = st.columns(5)
    a.metric("Stocks Tested", int(su.get("Successfully Tested", 0) or 0))
    b.metric("Total BUY Signals", int(su.get("Total BUY Signals", 0) or 0))
    c.metric("5D Success", "—" if su.get("5D Signal Success Rate %") is None else f"{float(su.get('5D Signal Success Rate %')):.1f}%")
    d.metric("10D Success", "—" if su.get("10D Signal Success Rate %") is None else f"{float(su.get('10D Signal Success Rate %')):.1f}%")
    e.metric("20D Success", "—" if su.get("20D Signal Success Rate %") is None else f"{float(su.get('20D Signal Success Rate %')):.1f}%")

    a,b,c,d,e = st.columns(5)
    a.metric("5D Avg Return", "—" if su.get("5D Signal Avg Return %") is None else f"{float(su.get('5D Signal Avg Return %')):+.2f}%")
    b.metric("10D Avg Return", "—" if su.get("10D Signal Avg Return %") is None else f"{float(su.get('10D Signal Avg Return %')):+.2f}%")
    c.metric("20D Avg Return", "—" if su.get("20D Signal Avg Return %") is None else f"{float(su.get('20D Signal Avg Return %')):+.2f}%")
    d.metric("Beat Buy & Hold", f"{float(su.get('Beat Buy & Hold %', 0) or 0):.1f}%")
    e.metric("Avg Outperformance", f"{float(su.get('Average Outperformance %', 0) or 0):+.2f}%")

    a,b,c,d = st.columns(4)
    a.metric("Positive Strategy", f"{float(su.get('Positive FLOWRIDE %', 0) or 0):.1f}%")
    b.metric("Avg Closed Win Rate", f"{float(su.get('Average Closed Trade Win Rate %', 0) or 0):.1f}%")
    c.metric("Avg Max Drawdown", f"{float(su.get('Average Max Drawdown %', 0) or 0):.1f}%")
    d.metric("Completed Trades", int(su.get("Total Completed Trades", 0) or 0))

    results = pd.DataFrame(ub.get("results", []) or [])
    if results.empty:
        st.warning("No stocks completed successfully. Check the failed/skipped list and backend logs.")
    else:
        st.markdown("### 🏆 BUY Signal Quality Ranking")
        st.caption("Ranking prioritizes 20-day BUY-signal success and return, then strategy outperformance.")
        st.dataframe(results, use_container_width=True, hide_index=True)

        chart_cols = [c for c in ["5D Success Rate %", "10D Success Rate %", "20D Success Rate %"] if c in results.columns]
        if chart_cols:
            chart_data = results[["Symbol"] + chart_cols].melt(
                id_vars="Symbol", var_name="Horizon", value_name="Success Rate %"
            ).dropna()
            if not chart_data.empty:
                fig_val = go.Figure()
                for horizon in chart_data["Horizon"].unique():
                    part = chart_data[chart_data["Horizon"] == horizon]
                    fig_val.add_trace(go.Bar(name=horizon, x=part["Symbol"], y=part["Success Rate %"]))
                fig_val.update_layout(
                    title="Historical FLOWRIDE BUY Signal Success by Horizon",
                    barmode="group",
                    xaxis_title="Stock",
                    yaxis_title="Success Rate %",
                    height=520,
                    margin=dict(l=10, r=10, t=50, b=10),
                )
                st.plotly_chart(fig_val, use_container_width=True, config={"displayModeBar": False})

        st.download_button(
            "⬇️ Download Strategy Validation CSV",
            results.to_csv(index=False).encode("utf-8"),
            file_name=f"flowride_validation_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Event-level EARLY WATCH / SETUP research export.
        # This is intentionally separate from the stock-level validation CSV.
        try:
            research_csv = call_bytes(
                "/signal_research_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if research_csv:
                st.download_button(
                    "🔬 Download Signal Research CSV",
                    research_csv,
                    file_name=f"flowride_signal_research_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"Signal Research CSV is not ready for this validation run: {e}")

        # EARLY WATCH V4 validation — intentionally separate from frozen V9 BUY metrics.
        # Uses the event-level signal research export produced by the same validation run.
        try:
            if research_csv:
                from io import BytesIO
                v4df = pd.read_csv(BytesIO(research_csv))

                # V4 is frozen: SETUP -> exactly 5 trading sessions -> survive if Day-5 close >= -1%.
                # Prefer backend V4 columns when present. Fall back to the research columns so this
                # panel remains auditable against the existing V3.2 survival export.
                if "EarlyWatchV4Day5ReturnPct" in v4df.columns:
                    day5 = pd.to_numeric(v4df["EarlyWatchV4Day5ReturnPct"], errors="coerce")
                elif "5D Confirmation Close Return %" in v4df.columns:
                    day5 = pd.to_numeric(v4df["5D Confirmation Close Return %"], errors="coerce")
                elif "Confirm 5D Close Return %" in v4df.columns:
                    day5 = pd.to_numeric(v4df["Confirm 5D Close Return %"], errors="coerce")
                else:
                    day5 = pd.Series(index=v4df.index, dtype=float)

                hit_col = next((c for c in [
                    "20D +10% Hit",
                    "Hit +10% within 20D"
                ] if c in v4df.columns), None)
                if hit_col:
                    hit10 = v4df[hit_col].astype(str).str.lower().isin(["true","1","yes"])
                else:
                    hit10 = pd.Series(False, index=v4df.index)

                usable = day5.notna()
                confirmed = usable & (day5 >= -1.0)
                failed_v4 = usable & ~confirmed
                winners = usable & hit10

                # A "false alert" is the backend's explicit FALSE_ALERT outcome,
                # not every event that failed to hit +10%. POSITIVE_20D events
                # remain a separate neutral/positive outcome class.
                if "Outcome Class" in v4df.columns:
                    false_alerts = usable & v4df["Outcome Class"].astype(str).eq("FALSE_ALERT")
                else:
                    false_alerts = usable & ~hit10

                winner_total = int(winners.sum())
                false_total = int(false_alerts.sum())
                winner_kept = int((winners & confirmed).sum())
                false_kept = int((false_alerts & confirmed).sum())

                winner_retention = (100.0 * winner_kept / winner_total) if winner_total else None
                false_reduction = (100.0 * (false_total - false_kept) / false_total) if false_total else None

                remaining_col = next((c for c in [
                    "5D Remaining 20D MFE From Confirmation %",
                    "Remaining 20D MFE From Confirm %",
                    "Remaining 20D MFE %",
                    "5D Remaining 20D MFE %",
                ] if c in v4df.columns), None)

                retained_winners = winners & confirmed
                avg_remaining = median_remaining = None
                if remaining_col and retained_winners.any():
                    rem = pd.to_numeric(v4df.loc[retained_winners, remaining_col], errors="coerce").dropna()
                    if not rem.empty:
                        avg_remaining = float(rem.mean())
                        median_remaining = float(rem.median())

                st.markdown("### 🧪 Early Watch V4 Validation")
                st.caption("Experimental layer only • Frozen rule: SETUP → wait 5 trading sessions → confirm when Day-5 close is ≥ −1% from SETUP close. V9 BUY / RIDE / EXIT are unchanged.")

                a,b,c,d = st.columns(4)
                a.metric("SETUP Events", int(len(v4df)))
                b.metric("Usable 5D Events", int(usable.sum()))
                c.metric("V4 Confirmed", int(confirmed.sum()))
                d.metric("V4 Failed", int(failed_v4.sum()))

                positive20_total = (
                    int((usable & v4df["Outcome Class"].astype(str).eq("POSITIVE_20D")).sum())
                    if "Outcome Class" in v4df.columns else 0
                )

                a,b,c,d = st.columns(4)
                a.metric("+10% Winners", winner_total)
                b.metric("Winners Retained", f"{winner_kept}/{winner_total}" if winner_total else "—")
                c.metric("Winner Retention", "—" if winner_retention is None else f"{winner_retention:.1f}%")
                d.metric("False-Alert Reduction", "—" if false_reduction is None else f"{false_reduction:.1f}%")

                a,b,c = st.columns(3)
                a.metric("False Alerts Retained", f"{false_kept}/{false_total}" if false_total else "—")
                b.metric("Avg Remaining 20D MFE", "—" if avg_remaining is None else f"{avg_remaining:+.2f}%")
                c.metric("Median Remaining 20D MFE", "—" if median_remaining is None else f"{median_remaining:+.2f}%")

                v4_view = v4df.loc[usable].copy()
                v4_view["V4 Result"] = ["CONFIRMED" if x else "FAILED" for x in confirmed.loc[usable]]
                show_cols = [c for c in [
                    "Symbol", "Signal Date", "Setup Date", "Close", "Setup Close",
                    "5D Confirmation Close Return %", "Confirm 5D Close Return %",
                    "EarlyWatchV4Day5ReturnPct", "V4 Result",
                    "20D +10% Hit", "Hit +10% within 20D",
                    remaining_col
                ] if c and c in v4_view.columns]
                if show_cols:
                    with st.expander("🔎 View Early Watch V4 events", expanded=False):
                        st.dataframe(v4_view[show_cols], use_container_width=True, hide_index=True)

        except Exception as e:
            st.warning(f"Early Watch V4 validation panel could not be calculated: {e}")

        # V4 -> V9 BUY linkage diagnostic. Research only; no strategy change.
        try:
            link_diag = ub.get("v4_to_v9_link_diagnostic", {}) or {}
            link_summary = link_diag.get("summary", {}) or {}
            if link_summary:
                st.markdown("### 🔗 Early Watch V4 → V9 BUY Diagnostic")
                st.caption("Links each frozen V4 confirmation to the subsequent frozen V9 BUY. Existing rides are separated from flat confirmations so they are not incorrectly counted as missed BUY conversions.")
                a,b,c,d = st.columns(4)
                a.metric("V4 Confirmed", link_summary.get("V4 Confirmed Events", "—"))
                b.metric("Already in FLOWRIDE", link_summary.get("Already In FLOWRIDE at Confirmation", "—"))
                conv = link_summary.get("Eligible Conversion Rate %")
                c.metric("Flat → V9 BUY ≤20D", "—" if conv is None else f"{float(conv):.1f}%")
                wconv = link_summary.get("Winner Conversion Rate %")
                d.metric("Winner Conversion ≤20D", "—" if wconv is None else f"{float(wconv):.1f}%")

                a,b = st.columns(2)
                med_days = link_summary.get("Median Trading Days Confirmation to BUY")
                med_gain = link_summary.get("Median Price Gain Confirmation to BUY %")
                a.metric("Median Confirmation → BUY", "—" if med_days is None else f"{float(med_days):.1f} trading days")
                b.metric("Median Gain Before BUY", "—" if med_gain is None else f"{float(med_gain):+.2f}%")

                blockers = link_summary.get("Top Blockers for No-BUY Events", {}) or {}
                if blockers:
                    bdf = pd.DataFrame([{"V9 Blocker":k,"No-BUY Event Count":v} for k,v in blockers.items()])
                    with st.expander("🚧 V9 blockers among V4 confirmations with no BUY within 20D", expanded=False):
                        st.dataframe(bdf, use_container_width=True, hide_index=True)

            link_csv = call_bytes(
                "/v4_v9_link_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if link_csv:
                st.download_button(
                    "🔗 Download V4 → V9 BUY Diagnostic CSV",
                    link_csv,
                    file_name=f"flowride_v4_to_v9_link_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V4 → V9 BUY diagnostic is not ready for this validation run: {e}")



        # V4 Entry Research V1. Research only; production strategy remains frozen.
        try:
            entry_research = ub.get("v4_entry_research_v1", {}) or {}
            entry_summary = entry_research.get("summary", {}) or {}
            if entry_summary:
                st.markdown("### 🧪 V4 Entry Research V1")
                st.caption("Tests simple early-entry filters after frozen Early Watch V4 confirmation. Primary outcome: +10% from the V4 confirmation close within the next 20 trading sessions. V9 BUY/RIDE/EXIT are unchanged.")
                a,b,c = st.columns(3)
                a.metric("Eligible V4 Confirmations", entry_summary.get("Eligible Flat Confirmations", "—"))
                b.metric("Post-confirmation +10% Winners", entry_summary.get("Post-Confirmation +10% Winners", "—"))
                br = entry_summary.get("Baseline Post-Confirmation +10% Rate %")
                c.metric("Baseline +10% Rate", "—" if br is None else f"{float(br):.1f}%")

                rules = entry_summary.get("rules", []) or []
                if rules:
                    rdf = pd.DataFrame(rules)
                    show = [c for c in [
                        "Rule","Selected","Post-Confirmation +10% Winners","Winner Retention %",
                        "Non-Winner Rejection %","Precision %","Avg Remaining 20D MFE %",
                        "Median Remaining 20D MFE %","Avg Remaining 20D MAE %"
                    ] if c in rdf.columns]
                    st.dataframe(rdf[show], use_container_width=True, hide_index=True)

            entry_csv = call_bytes(
                "/v4_entry_research_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if entry_csv:
                st.download_button(
                    "🧪 Download V4 Entry Research V1 CSV",
                    entry_csv,
                    file_name=f"flowride_v4_entry_research_v1_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V4 Entry Research V1 is not ready for this validation run: {e}")

        # V9 Profit Protection Research V5 — research only.
        try:
            pp = ub.get("v9_profit_protection_research_v5", {}) or {}
            ps = pp.get("summary", {}) or {}
            variants = ps.get("variants", []) or []
            if variants:
                st.markdown("### 🛡️ V9 Profit Protection Research V5")
                st.caption(
                    "Research only. Within each fixed entry family, compares the current V3.1 "
                    "profit floor with BALANCED and TIGHT winner-protection schedules. "
                    "Production BUY/RIDE/EXIT remains unchanged."
                )

                vdf = pd.DataFrame(variants)
                show_cols = [c for c in [
                    "Entry Family","Protection Profile","Completed Trades","Winning Trades",
                    "Win Rate %","Avg Return %","Avg MFE %","Avg MAE %",
                    "Avg Giveback pp","Reached +10% MFE","+10% MFE -> <=0 Exit",
                    "Winner-to-Loser %","+10% Retention %","Reached +20% MFE",
                    "+20% Retention %","Delta Avg Return vs Control pp",
                    "Delta Win Rate vs Control pp","Delta Giveback vs Control pp",
                    "Delta Winner-to-Loser vs Control pp"
                ] if c in vdf.columns]
                st.dataframe(vdf[show_cols], use_container_width=True, hide_index=True)

                paths = ps.get("winner_path", []) or []
                if paths:
                    with st.expander("Winner path by MFE band"):
                        st.dataframe(pd.DataFrame(paths), use_container_width=True, hide_index=True)

                reasons = ps.get("exit_reasons", []) or []
                if reasons:
                    with st.expander("Exit reason comparison"):
                        st.dataframe(pd.DataFrame(reasons), use_container_width=True, hide_index=True)

            params = {
                "exchange": ub.get("exchange", ub_exchange),
                "period": ub.get("period", ub_period),
                "sample_seed": int(su.get("Sample Seed", ub_seed)),
            }

            raw = call_bytes("/v9_profit_protection_research_v5_csv", params, timeout=180)
            if raw:
                st.download_button(
                    "🛡️ Download Profit Protection V5 Summary CSV",
                    raw,
                    file_name=f"flowride_v9_profit_protection_research_v5_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',357)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            raw_trades = call_bytes("/v9_profit_protection_research_v5_trades_csv", params, timeout=180)
            if raw_trades:
                st.download_button(
                    "🔬 Download Profit Protection V5 Trade-Level CSV",
                    raw_trades,
                    file_name=f"flowride_v9_profit_protection_trades_v5_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',357)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V9 Profit Protection Research V5 is not ready: {e}")

        # V9 Profit Capture Research V4 — research only.
        try:
            pc = ub.get("v9_profit_capture_research_v4", {}) or {}
            ps = pc.get("summary", {}) or {}
            variants = ps.get("variants", []) or []
            if variants:
                st.markdown("### 🎯 V9 Profit Capture Research V4")
                st.caption("Research only. Compares BASE 55–68, CHALLENGER 60–72 and AGGRESSIVE ≥60 with the same RIDE Manager V3.1. Focus: how much MFE is surrendered before EXIT.")
                pdf = pd.DataFrame(variants)
                cols = [c for c in [
                    "Variant","Completed Trades","Winning Trades","Win Rate %","Avg Return %",
                    "Avg MFE %","Avg MAE %","Avg Giveback pp","Avg Peak Capture %",
                    "Avg Peak-to-Exit Sessions","Trades Reaching +10% MFE",
                    "+10% MFE Then Non-Positive Exit","Winner-Loss Conversion %"
                ] if c in pdf.columns]
                st.dataframe(pdf[cols], use_container_width=True, hide_index=True)

                buckets = ps.get("mfe_buckets", []) or []
                if buckets:
                    with st.expander("MFE bucket diagnostics"):
                        st.dataframe(pd.DataFrame(buckets), use_container_width=True, hide_index=True)

                reasons = ps.get("exit_reasons", []) or []
                if reasons:
                    with st.expander("Exit reason diagnostics"):
                        st.dataframe(pd.DataFrame(reasons), use_container_width=True, hide_index=True)

            params = {
                "exchange": ub.get("exchange", ub_exchange),
                "period": ub.get("period", ub_period),
                "sample_seed": int(su.get("Sample Seed", ub_seed)),
            }
            raw = call_bytes("/v9_profit_capture_research_v4_csv", params, timeout=180)
            if raw:
                st.download_button(
                    "🎯 Download Profit Capture V4 Summary CSV",
                    raw,
                    file_name=f"flowride_v9_profit_capture_research_v4_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',357)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            raw_trades = call_bytes("/v9_profit_capture_research_v4_trades_csv", params, timeout=180)
            if raw_trades:
                st.download_button(
                    "🔬 Download Profit Capture V4 Trade-Level CSV",
                    raw_trades,
                    file_name=f"flowride_v9_profit_capture_trades_v4_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',357)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V9 Profit Capture Research V4 is not ready: {e}")

        # V9 RSI Threshold Experiment V3 — research only.
        try:
            ex = ub.get("v9_rsi_threshold_experiment_v3", {}) or {}
            sm = ex.get("summary", {}) or {}
            rows = sm.get("rows", []) or []
            if rows:
                st.markdown("### 🧪 V9 RSI Threshold Experiment V3")
                st.caption("Controlled strategy experiment: only the RSI BUY window changes. All other V9 gates, 2-candle confirmation, and RIDE Manager V3.1 exits stay identical.")
                edf = pd.DataFrame(rows)
                cols = [c for c in [
                    "Variant","BUY Signals","Completed Trades","Winning Trades","Win Rate %",
                    "Avg Return %","Median Return %","Avg MFE %","Avg MAE %","Avg Giveback pp",
                    "Δ BUY vs Base","Δ Winners vs Base","Δ Win Rate pp","Δ Avg Return pp","Δ Avg MAE pp"
                ] if c in edf.columns]
                st.dataframe(edf[cols], use_container_width=True, hide_index=True)

            raw = call_bytes(
                "/v9_rsi_threshold_experiment_v3_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if raw:
                st.download_button(
                    "🧪 Download V9 RSI Threshold Experiment V3 CSV",
                    raw,
                    file_name=f"flowride_v9_rsi_threshold_experiment_v3_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V9 RSI Threshold Experiment V3 is not ready: {e}")

        # V9 RSI Research V2 — research only.
        try:
            rr = ub.get("v9_rsi_research_v2", {}) or {}
            rs = rr.get("summary", {}) or {}
            if rs:
                st.markdown("### 🧭 V9 RSI Research V2")
                st.caption("Research only. RSI14 is split into bands at frozen V4 confirmation. The primary outcome is a fresh +10% move from the V4 confirmation price over the next 20 sessions. Production V9 RSI 55–68 is unchanged.")

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Eligible V4 Events", rs.get("events", "—"))
                c2.metric("Post-V4 +10% Winners", rs.get("post_v4_10pct_winners", "—"))
                br = rs.get("post_v4_baseline_success_rate_pct")
                c3.metric("Post-V4 Baseline", "—" if br is None else f"{float(br):.1f}%")
                obr = rs.get("setup_based_baseline_success_rate_pct")
                c4.metric("Setup-Based Baseline", "—" if obr is None else f"{float(obr):.1f}%")

                bands = rs.get("bands", []) or []
                if bands:
                    rdf = pd.DataFrame(bands)
                    cols = [c for c in [
                        "RSI Band","Events","Post-V4 +10% Winners","Post-V4 +10% Success Rate %",
                        "Setup-Based +10% Success Rate %","Avg Post-V4 20D MFE %",
                        "Median Post-V4 20D MFE %","Avg Post-V4 20D MAE %",
                        "Median Post-V4 20D MAE %","V9 BUY Within 20D","V9 BUY Conversion %","Avg RSI"
                    ] if c in rdf.columns]
                    st.dataframe(rdf[cols], use_container_width=True, hide_index=True)

            raw = call_bytes(
                "/v9_rsi_research_v2_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if raw:
                st.download_button(
                    "🧭 Download V9 RSI Research V2 CSV",
                    raw,
                    file_name=f"flowride_v9_rsi_research_v2_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V9 RSI Research V2 is not ready: {e}")

        # V9 BUY Condition Research V1 — research only.
        try:
            vr=ub.get("v9_buy_condition_research_v1",{}) or {}
            vs=vr.get("summary",{}) or {}
            if vs:
                st.markdown("### 🔬 V9 BUY Condition Research V1")
                st.caption("Ranks each frozen V9 gate by outcome quality versus winners blocked. No production BUY rule is changed.")
                c1,c2,c3=st.columns(3)
                c1.metric("Eligible V4 Events",vs.get("events","—"))
                c2.metric("+10% Winners",vs.get("eventual_10pct_winners","—"))
                br=vs.get("baseline_success_rate_pct")
                c3.metric("Baseline +10% Rate","—" if br is None else f"{float(br):.1f}%")
                rr=vs.get("conditions",[]) or []
                if rr:
                    rdf=pd.DataFrame(rr)
                    cols=[c for c in ["Condition","Events Passing","Pass Rate %","Success Rate When Pass %",
                                      "Success Rate When Fail %","Quality Lift pp","Winner Retention %",
                                      "Winners Blocked","Non-Winners Blocked","Blocked Winner Share %"] if c in rdf.columns]
                    st.dataframe(rdf[cols],use_container_width=True,hide_index=True)
            raw=call_bytes("/v9_buy_condition_research_csv",
                {"exchange":ub.get("exchange",ub_exchange),"period":ub.get("period",ub_period),
                 "sample_seed":int(su.get("Sample Seed",ub_seed))},timeout=180)
            if raw:
                st.download_button("🔬 Download V9 BUY Condition Research CSV",raw,
                    file_name=f"flowride_v9_buy_condition_research_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",use_container_width=True)
        except Exception as e:
            st.warning(f"V9 BUY Condition Research is not ready: {e}. If the CSV is empty, deploy the matching fixed backend and rerun validation.")

        # V4 Entry Research V3 — post-confirmation survival/follow-through.
        try:
            v3 = ub.get("v4_entry_research_v3", {}) or {}
            v3s = v3.get("summary", {}) or {}
            if v3s:
                st.markdown("### 🧪 V4 Entry Research V3 — 1D/2D/3D Follow-Through")
                st.caption("Research only. Tests the first 1–3 sessions after frozen V4 confirmation. Remaining +10% performance is measured from the actual decision close, not from the earlier V4 price. Production V9 BUY/RIDE/EXIT are unchanged.")
                a,b,c,d = st.columns(4)
                a.metric("Eligible V4 Confirmations", v3s.get("Eligible Flat Confirmations", "—"))
                b1 = v3s.get("1D Baseline +10% Rate %")
                b.metric("1D Baseline +10%", "—" if b1 is None else f"{float(b1):.1f}%")
                b2 = v3s.get("2D Baseline +10% Rate %")
                c.metric("2D Baseline +10%", "—" if b2 is None else f"{float(b2):.1f}%")
                b3 = v3s.get("3D Baseline +10% Rate %")
                d.metric("3D Baseline +10%", "—" if b3 is None else f"{float(b3):.1f}%")

                rules = v3s.get("rules", []) or []
                if rules:
                    rdf = pd.DataFrame(rules)
                    show = [c for c in [
                        "Rule","Decision Day","Selected","Remaining +10% Winners","Precision %",
                        "Winner Retention %","Non-Winner Rejection %","Avg Remaining 20D MFE %",
                        "Median Remaining 20D MFE %","Avg Remaining 20D MAE %"
                    ] if c in rdf.columns]
                    st.dataframe(rdf[show], use_container_width=True, hide_index=True)

            v3_csv = call_bytes(
                "/v4_entry_v3_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if v3_csv:
                st.download_button(
                    "🧪 Download V4 Entry Research V3 CSV",
                    v3_csv,
                    file_name=f"flowride_v4_entry_research_v3_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"V4 Entry Research V3 is not ready for this validation run: {e}")

        # Event-level EXIT/RIDE research export.
        # Measures premature exits and repeated re-BUY behaviour without changing strategy rules.
        try:
            exit_ride_csv = call_bytes(
                "/exit_ride_research_csv",
                {
                    "exchange": ub.get("exchange", ub_exchange),
                    "period": ub.get("period", ub_period),
                    "sample_seed": int(su.get("Sample Seed", ub_seed)),
                },
                timeout=180,
            )
            if exit_ride_csv:
                st.download_button(
                    "🏄 Download EXIT/RIDE Research CSV",
                    exit_ride_csv,
                    file_name=f"flowride_exit_ride_research_{ub.get('exchange','NSE')}_{ub.get('period','2y')}_seed_{su.get('Sample Seed',89)}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception as e:
            st.warning(f"EXIT/RIDE Research CSV is not ready for this validation run: {e}")

    failures = pd.DataFrame(ub.get("failures", []) or [])
    if not failures.empty:
        with st.expander(f"⚠️ Failed / skipped stocks ({len(failures)})", expanded=False):
            st.dataframe(failures, use_container_width=True, hide_index=True)

    with st.expander("ℹ️ How to read the success rate", expanded=False):
        st.write("• 5D / 10D / 20D Success Rate = percentage of historical FLOWRIDE BUY signals with a positive close-to-close return after that many trading days.")
        st.write("• Closed Trade Win Rate = percentage of completed BUY → EXIT trades that were profitable.")
        st.write("• These are different metrics. A low closed-trade win rate does not automatically mean the BUY signal itself is weak.")
        st.write("• Use different Sample Seed values to test multiple representative universe samples.")

    with st.expander("⚙️ Validation assumptions", expanded=False):
        for item in ub.get("assumptions", []) or []:
            st.write(f"• {item}")

st.divider()
st.subheader("🚀 Ranked Opportunity Scanner")
st.caption("Live scanner • V9 strategy logic unchanged. FLAT means no active ride; EXIT is shown only when an actual EXIT event occurs on the latest candle. Early Watch V4 remains separate.")
scan_ex = st.selectbox("Exchange for scan", ["NSE", "BSE"], key="scan_exchange")
limit = st.select_slider("Stocks to scan", options=[25,50,100,250,300], value=50, key="scan_limit")
if st.button("🔄 RUN EOD SCAN", type="primary", use_container_width=True):
    try:
        with st.spinner(f"Running FAST EOD scan for {limit} {scan_ex} securities…"):
            raw = call("/scan", {"exchange": scan_ex, "limit": int(limit)}, timeout=600)
        rows = raw.get("results", raw) if isinstance(raw, dict) else raw
        if not isinstance(rows, list): raise RuntimeError("Unexpected scan response from backend")
        df = pd.DataFrame(rows)
        if df.empty:
            st.warning("No usable securities returned from this scan batch.")
        else:
            rename = {
                "Symbol":"symbol","Company":"name","Exchange":"exchange","Close":"close",
                "Score":"score","Signal":"signal","FLOWRIDE":"flowride",
                "Early Watch V4":"early_watch_v4","V4 Confirmed":"v4_confirmed",
                "V4 Failed":"v4_failed","V4 Setup Date":"v4_setup_date",
                "V4 Day5 Return %":"v4_day5_return_pct",
                "Flow Score":"flow_score","RSI":"rsi","ATR %":"atr_pct"
            }
            df = df.rename(columns=rename)
            st.session_state.scan = df
            st.success(f"Scan complete • {len(df)} usable securities")
    except Exception as e:
        st.error(f"Scan failed: {e}")

if "scan" in st.session_state:
    df = st.session_state.scan.copy()
    if not df.empty:
        # Production FLOWRIDE states and experimental Early Watch states are
        # deliberately shown separately so V4 never masquerades as a BUY.
        flow = df["flowride"] if "flowride" in df.columns else pd.Series("", index=df.index)
        ew = df["early_watch_v4"] if "early_watch_v4" in df.columns else pd.Series("NONE", index=df.index)

        a,b,c,d,e = st.columns(5)
        a.metric("Stocks", len(df))
        b.metric("🟢 BUY", int((flow=="BUY").sum()))
        c.metric("🔵 RIDE", int((flow=="RIDE").sum()))
        d.metric("🔴 EXIT Today", int((flow=="EXIT").sum()))
        e.metric("⚪ FLAT", int((flow=="FLAT").sum()))

        st.markdown("#### 🧪 Early Watch V4 — current candidates")
        a,b,c,d = st.columns(4)
        a.metric("🟣 V4 Confirmed", int((ew=="EARLY WATCH V4").sum()))
        b.metric("🟡 Observation", int((ew=="OBSERVATION").sum()))
        c.metric("⚪ New SETUP", int((ew=="SETUP").sum()))
        d.metric("Failed Today", int((ew=="FAILED").sum()))
        st.caption("Experimental only • SETUP → 5 trading-session observation → confirm if Day-5 close is ≥ −1% from SETUP close. This does not replace a V9 BUY.")

        active_v4 = df[ew.isin(["EARLY WATCH V4","OBSERVATION","SETUP"])].copy()
        if active_v4.empty:
            st.info("No active Early Watch V4 candidates in this scan batch today.")
        else:
            v4_cols = [c for c in [
                "symbol","name","exchange","close","early_watch_v4","v4_setup_date",
                "v4_day5_return_pct","flowride","flow_score","rsi","atr_pct"
            ] if c in active_v4.columns]
            st.dataframe(active_v4[v4_cols], use_container_width=True, hide_index=True)

        st.markdown("#### 🏆 FLOWRIDE ranked opportunities")
        cols = [c for c in [
            "symbol","name","exchange","close","score","signal","flowride",
            "early_watch_v4","flow_score","rsi","atr_pct"
        ] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download scan CSV", df.to_csv(index=False).encode("utf-8"), "flowride_scan.csv", "text/csv", use_container_width=True)

st.divider()
st.markdown("### About Stocks Rides")
st.markdown("**🟢 BUY → 🔵 RIDE → 🔴 EXIT**")
st.caption("Stocks Rides is a rules-based technical market-analysis system. Historical/delayed data may not be real-time. It is not personalized investment advice.")
st.caption(f"{APP_VERSION}")
