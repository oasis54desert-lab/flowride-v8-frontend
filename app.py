import os
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

APP_VERSION = "V8.1-FLOWRIDE-CHART-DASHBOARD"
API_URL = os.getenv("FLOWRIDE_API_URL", "").rstrip("/")
API_KEY = os.getenv("FLOWRIDE_API_KEY", "")
try:
    API_URL = st.secrets.get("FLOWRIDE_API_URL", API_URL).rstrip("/")
    API_KEY = st.secrets.get("FLOWRIDE_API_KEY", API_KEY)
except Exception:
    pass

st.set_page_config(page_title="Indian Stock Scanner FLOWRIDE", page_icon="🇮🇳", layout="centered")

st.markdown("""
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1100px;}
.hero-title {font-size: 2.25rem; font-weight: 800; line-height: 1.05; margin-bottom: .35rem;}
.hero-sub {font-size: 1rem; opacity: .72; margin-bottom: 1rem;}
.status {padding: .8rem 1rem; border-radius: 12px; background: rgba(35,116,190,.18); border: 1px solid rgba(35,116,190,.35);}
.flow-card {padding: 18px; border-radius: 16px; text-align:center; margin: 10px 0 18px 0;}
.flow-buy {background:#dff6e7; color:#126b36; border:1px solid #8dd5a6;}
.flow-ride {background:#e3efff; color:#1559a6; border:1px solid #8db7ef;}
.flow-exit {background:#ffe3e3; color:#a51f1f; border:1px solid #ef9a9a;}
.flow-state {font-size: 30px; font-weight: 800;}
.flow-score {font-size: 15px; font-weight: 650; margin-top: 5px;}
.section-title {margin-top: 1rem;}
@media (max-width: 600px) {
  .hero-title {font-size: 1.9rem;}
  .flow-state {font-size: 26px;}
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">🇮🇳 Indian Stock Scanner</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">FLOWRIDE • Find the trend. <b>Ride the flow.</b> Exit when it breaks.</div>', unsafe_allow_html=True)

if not API_URL or not API_KEY:
    st.error("Backend configuration is missing. Set FLOWRIDE_API_URL and FLOWRIDE_API_KEY in Streamlit Secrets.")
    st.stop()

def call(path, params=None, timeout=90):
    r = requests.get(API_URL + path, params=params or {}, headers={"X-API-Key": API_KEY}, timeout=timeout)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(str(detail))
    return r.json()

try:
    h = requests.get(API_URL + "/health", timeout=20).json()
    st.markdown(f'<div class="status">Backend: <b>ONLINE</b> • {h.get("version", "unknown")}<br>Universe: <b>{h.get("total", 0):,}</b> securities • NSE <b>{h.get("nse", 0):,}</b> • BSE <b>{h.get("bse", 0):,}</b></div>', unsafe_allow_html=True)
except Exception:
    st.warning("Backend is waking up or unavailable. Try again in a moment.")

st.markdown('<h3 class="section-title">🔎 Search Stock</h3>', unsafe_allow_html=True)
q = st.text_input("Search NSE/BSE symbol, company name or scrip code", placeholder="RELIANCE, TCS, PRICOL, 500325...", label_visibility="visible")
ex = st.selectbox("Exchange", ["ALL", "NSE", "BSE"])
if st.button("🔍 SEARCH", type="primary", use_container_width=True) and q.strip():
    try:
        raw = call("/search", {"q": q.strip(), "exchange": ex})
        results = raw.get("results", raw) if isinstance(raw, dict) else raw
        if not isinstance(results, list):
            raise RuntimeError("Unexpected search response from backend")
        st.session_state.results = results
        st.session_state.pop("analysis", None)
        st.success(f"Found {len(results)} matching securities.")
    except Exception as e:
        st.error(f"Search failed: {e}")

results = st.session_state.get("results", [])
if results:
    labels = [f"{r['symbol']} — {r['name']} ({r['exchange']})" for r in results]
    idx = st.selectbox("Select stock", range(len(labels)), format_func=lambda i: labels[i])
    sel = results[idx]
    if st.button("📊 ANALYZE SELECTED STOCK", type="primary", use_container_width=True):
        try:
            with st.spinner("Loading market data and analysis…"):
                st.session_state.analysis = call("/analyze", {"exchange": sel["exchange"], "symbol": sel["symbol"]}, timeout=120)
        except Exception as e:
            st.error(f"Analysis failed: {e}")

analysis = st.session_state.get("analysis")
if analysis:
    st.divider()
    st.subheader(f"📊 {analysis['name']} | {analysis['symbol']} ({analysis['exchange']})")
    st.caption(f"Yahoo ticker: `{analysis.get('ticker','—')}` • Latest data: {analysis.get('latest_date','—')}")

    flow = analysis.get("flowride", {})
    state = str(flow.get("state", "RIDE")).upper()
    icon = "🟢" if state == "BUY" else "🔴" if state == "EXIT" else "🔵"
    cls = "flow-buy" if state == "BUY" else "flow-exit" if state == "EXIT" else "flow-ride"
    score = float(flow.get("score", 0) or 0)
    st.markdown(f'<div class="flow-card {cls}"><div class="flow-state">{icon} {state}</div><div class="flow-score">FLOWRIDE Flow Score {score:.0f}/100</div></div>', unsafe_allow_html=True)

    m = analysis.get("metrics", {})
    c = st.columns(4)
    c[0].metric("Close", f"₹{float(m.get('price',0)):,.2f}")
    c[1].metric("Score", f"{float(m.get('score',0)):.0f}/100")
    c[2].metric("Signal", str(m.get("signal", "—")))
    c[3].metric("RSI", f"{float(m['rsi']):.1f}" if m.get("rsi") is not None else "—")

    c = st.columns(4)
    c[0].metric("ATR", f"₹{float(m.get('atr',0)):,.2f}")
    c[1].metric("ATR %", f"{float(m.get('atrpct',0)):.2f}%" if m.get("atrpct") is not None else "—")
    c[2].metric("Stop Loss", f"₹{float(m.get('stop',0)):,.2f}")
    c[3].metric("Target 1", f"₹{float(m.get('target1',0)):,.2f}")

    c = st.columns(3)
    c[0].metric("Target 2", f"₹{float(m.get('target2',0)):,.2f}")
    c[1].metric("Flow Entry", f"₹{float(flow['entry']):,.2f}" if flow.get("entry") is not None else "—")
    c[2].metric("Trailing Flow Stop", f"₹{float(flow.get('trail',0)):,.2f}")

    chart = analysis.get("chart", {})
    dates = chart.get("date", [])
    if dates:
        st.markdown("### 📈 Technical Dashboard")
        days = st.slider("Chart period (days)", 60, min(500, len(dates)), min(180, len(dates)), 10)
        sl = slice(max(0, len(dates)-days), len(dates))
        d = pd.DataFrame({
            "Date": pd.to_datetime(dates[sl]),
            "Open": chart.get("open", [None]*len(dates))[sl],
            "High": chart.get("high", [None]*len(dates))[sl],
            "Low": chart.get("low", [None]*len(dates))[sl],
            "Close": chart.get("price", [None]*len(dates))[sl],
            "Volume": chart.get("volume", [None]*len(dates))[sl],
            "SMA20": chart.get("sma20", [None]*len(dates))[sl],
            "SMA50": chart.get("sma50", [None]*len(dates))[sl],
            "SMA200": chart.get("sma200", [None]*len(dates))[sl],
            "EMA20": chart.get("ema20", [None]*len(dates))[sl],
            "EMA50": chart.get("ema50", [None]*len(dates))[sl],
            "BBUpper": chart.get("bb_upper", [None]*len(dates))[sl],
            "BBLower": chart.get("bb_lower", [None]*len(dates))[sl],
            "RSI": chart.get("rsi14", [None]*len(dates))[sl],
            "MACD": chart.get("macd", [None]*len(dates))[sl],
            "MACDSignal": chart.get("macd_signal", [None]*len(dates))[sl],
            "MACDHist": chart.get("macd_hist", [None]*len(dates))[sl],
            "RIDE": chart.get("ride", [None]*len(dates))[sl],
            "BUY": chart.get("buy", [None]*len(dates))[sl],
            "EXIT": chart.get("exit", [None]*len(dates))[sl],
        }).set_index("Date")

        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.025,
                            row_heights=[0.52, 0.16, 0.16, 0.16],
                            subplot_titles=("Price / Trend / Bollinger", "Volume", "RSI (14)", "MACD"))
        fig.add_trace(go.Candlestick(x=d.index, open=d.Open, high=d.High, low=d.Low, close=d.Close, name="Candles"), row=1, col=1)
        for col, name in [("SMA20","SMA 20"),("SMA50","SMA 50"),("SMA200","SMA 200"),("EMA20","EMA 20"),("EMA50","EMA 50"),("BBUpper","BB Upper"),("BBLower","BB Lower")]:
            fig.add_trace(go.Scatter(x=d.index, y=d[col], mode="lines", name=name), row=1, col=1)
        fig.add_trace(go.Scatter(x=d.index, y=d.RIDE, mode="markers", name="RIDE", marker=dict(size=4)), row=1, col=1)
        fig.add_trace(go.Scatter(x=d.index, y=d.BUY, mode="markers", name="BUY", marker=dict(size=10, symbol="triangle-up")), row=1, col=1)
        fig.add_trace(go.Scatter(x=d.index, y=d.EXIT, mode="markers", name="EXIT", marker=dict(size=10, symbol="triangle-down")), row=1, col=1)
        fig.add_trace(go.Bar(x=d.index, y=d.Volume, name="Volume"), row=2, col=1)
        fig.add_trace(go.Scatter(x=d.index, y=d.RSI, mode="lines", name="RSI"), row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", row=3, col=1)
        fig.add_trace(go.Scatter(x=d.index, y=d.MACD, mode="lines", name="MACD"), row=4, col=1)
        fig.add_trace(go.Scatter(x=d.index, y=d.MACDSignal, mode="lines", name="Signal"), row=4, col=1)
        fig.add_trace(go.Bar(x=d.index, y=d.MACDHist, name="Histogram"), row=4, col=1)
        fig.update_layout(height=980, xaxis_rangeslider_visible=False, hovermode="x unified",
                          legend=dict(orientation="h"), margin=dict(l=10,r=10,t=65,b=10))
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0,100], row=3, col=1)
        st.plotly_chart(fig, use_container_width=True)

    reasons = m.get("reasons", []) or []
    if reasons:
        st.info("Positive factors: " + " • ".join(reasons))

st.divider()
st.subheader("🚀 Ranked Universe Scanner")
scan_ex = st.selectbox("Exchange for scan", ["NSE", "BSE"], key="scan_ex")
limit = st.number_input("Stocks to scan", min_value=10, max_value=300, value=50, step=10)
if st.button("🔄 RUN EOD SCAN", type="primary", use_container_width=True):
    try:
        with st.spinner(f"Scanning {limit} {scan_ex} securities…"):
            data = call("/scan", {"exchange": scan_ex, "limit": int(limit)}, timeout=240)
        out = pd.DataFrame(data.get("results", []))
        st.success(f"Usable: {data.get('usable', len(out))} • Failed/unavailable: {data.get('failed', 0)}")
        if not out.empty:
            cols = [c for c in ["symbol","name","exchange","close","score","signal","flowride","flow_score","rsi","atr_pct","stop_loss","target1"] if c in out.columns]
            st.dataframe(out[cols].round(2), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Scan failed: {e}")

st.caption("FLOWRIDE is a rules-based technical market-analysis system. It is not personalized investment advice.")
