import os
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

APP_VERSION = "V8.3-FLOWRIDE-SINGLE-FLOW-FRONTEND"
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

st.set_page_config(page_title="Indian Stock Scanner PRO", page_icon="📈", layout="wide")

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

st.markdown('<div class="hero"><div class="hero-title">🇮🇳 Indian Stock Scanner <span style="font-size:.48em;opacity:.7">PRO</span></div><div class="hero-sub">FLOWRIDE • Find the trend. <b>Ride the flow.</b> Exit when it breaks.</div></div>', unsafe_allow_html=True)

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
except Exception as e:
    st.warning("Backend is waking up or unavailable. Try again in a moment.")

with st.sidebar:
    st.markdown("## FLOWRIDE PRO")
    st.caption("Simple signals. Advanced analysis stays on the private server.")
    st.markdown("🟢 **BUY**  •  🔵 **RIDE**  •  🔴 **EXIT**")
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
    st.caption(f"Yahoo ticker: `{analysis.get('ticker','—')}` • Latest data: {analysis.get('latest_date','—')}")
    state = str(f.get("state", "RIDE")).upper()
    state_label = "🟢 BUY" if state == "BUY" else "🔵 RIDE" if state == "RIDE" else "🔴 EXIT"
    cls = "flow-buy" if state == "BUY" else "flow-exit" if state == "EXIT" else "flow-ride"
    st.markdown(f'<div class="flow-card {cls}"><div class="flow-state">{state_label}</div><div class="flow-score">FLOWRIDE Flow Score {float(f.get("score",0) or 0):.0f}/100</div></div>', unsafe_allow_html=True)

    a,b,c,d,e = st.columns(5)
    a.metric("Close", f"₹{float(m.get('price',0)):,.2f}")
    b.metric("Score", f"{float(m.get('score',0)):.0f}/100")
    c.metric("Signal", str(m.get("signal", "—")))
    d.metric("RSI", f"{float(m['rsi']):.1f}" if m.get("rsi") is not None else "—")
    e.metric("FLOWRIDE", state_label)
    a,b,c = st.columns(3)
    a.metric("Flow Score", f"{float(f.get('score',0) or 0):.0f}/100")
    b.metric("Trailing Flow Stop", f"₹{float(f.get('trail',0) or 0):,.2f}")
    c.metric("Entry Reference", f"₹{float(f['entry']):,.2f}" if f.get("entry") is not None else "—")

    chart = analysis.get("chart", {})
    dates = chart.get("date", [])
    if dates:
        st.markdown("### 🌊 FLOWRIDE — BUY → RIDE → EXIT")
        st.caption("One confirmed BUY starts the flow. Blue RIDE continues it. One confirmed EXIT ends it. No repeated BUY/EXIT markers during the same flow.")
        flow_days = st.slider("FLOWRIDE chart period (days)", 60, min(500, len(dates)), min(180, len(dates)), 10, key="flow_chart_days")
        start = max(0, len(dates)-flow_days)
        fd = pd.DataFrame({
            "Date": pd.to_datetime(dates[start:]),
            "Price": chart.get("price", [None]*len(dates))[start:],
            "Flow": chart.get("flow_line", [None]*len(dates))[start:],
            "BUY": chart.get("buy", [None]*len(dates))[start:],
            "EXIT": chart.get("exit", [None]*len(dates))[start:],
        }).set_index("Date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fd.index, y=fd.Price, mode="lines", name="Price", line=dict(width=1.5)))
        fig.add_trace(go.Scatter(x=fd.index, y=fd.Flow, mode="lines", name="RIDE FLOW", connectgaps=False, line=dict(width=4)))
        bx = fd.index[fd.BUY.notna()]; by = fd.loc[bx, "BUY"]
        exx = fd.index[fd.EXIT.notna()]; ey = fd.loc[exx, "EXIT"]
        if len(bx): fig.add_trace(go.Scatter(x=bx, y=by, mode="markers+text", name="BUY", marker=dict(size=13, symbol="triangle-up"), text=["BUY"]*len(bx), textposition="top center"))
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
st.subheader("🚀 Ranked Universe Scanner")
scan_ex = st.selectbox("Exchange for scan", ["NSE", "BSE"], key="scan_exchange")
limit = st.select_slider("Stocks to scan", options=[25,50,100,250,300], value=50, key="scan_limit")
if st.button("🔄 RUN EOD SCAN", type="primary", use_container_width=True):
    try:
        with st.spinner(f"Running secure server-side EOD scan for {limit} {scan_ex} securities…"):
            raw = call("/scan", {"exchange": scan_ex, "limit": int(limit)}, timeout=600)
        rows = raw.get("results", raw) if isinstance(raw, dict) else raw
        if not isinstance(rows, list): raise RuntimeError("Unexpected scan response from backend")
        df = pd.DataFrame(rows)
        if df.empty:
            st.warning("No usable securities returned from this scan batch.")
        else:
            rename = {"Symbol":"symbol","Company":"name","Exchange":"exchange","Close":"close","Score":"score","Signal":"signal","FLOWRIDE":"flowride","Flow Score":"flow_score","RSI":"rsi","ATR %":"atr_pct"}
            df = df.rename(columns=rename)
            st.session_state.scan = df
            st.success(f"Scan complete • {len(df)} usable securities")
    except Exception as e:
        st.error(f"Scan failed: {e}")

if "scan" in st.session_state:
    df = st.session_state.scan.copy()
    if not df.empty:
        a,b,c,d = st.columns(4)
        a.metric("Stocks", len(df)); b.metric("🟢 BUY", int((df.get("flowride","")=="BUY").sum())); c.metric("🔵 RIDE", int((df.get("flowride","")=="RIDE").sum())); d.metric("🔴 EXIT", int((df.get("flowride","")=="EXIT").sum()))
        st.markdown("#### Top opportunities")
        cols = [c for c in ["symbol","name","exchange","close","score","signal","flowride","flow_score","rsi","atr_pct"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download scan CSV", df.to_csv(index=False).encode("utf-8"), "flowride_scan.csv", "text/csv", use_container_width=True)

st.divider()
st.markdown("### About FLOWRIDE")
st.markdown("**🟢 BUY → 🔵 RIDE → 🔴 EXIT**")
st.caption("FLOWRIDE is a rules-based technical market-analysis system. Historical/delayed data may not be real-time. It is not personalized investment advice.")
st.caption(f"{APP_VERSION}")
