import os
import requests
import pandas as pd
import streamlit as st

APP_VERSION = "V8.0.1-FLOWRIDE-CUSTOMER"
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
div.stButton>button{width:100%;border-radius:10px;font-weight:600}
.flow{padding:14px;border-radius:12px;text-align:center;font-size:25px;font-weight:700;background:#eef5ff}
</style>
""", unsafe_allow_html=True)

st.title("🇮🇳 Indian Stock Scanner")
st.caption("FLOWRIDE • Find the trend. Ride the flow. Exit when it breaks.")

if not API_URL or not API_KEY:
    st.error("Backend configuration is missing. Set FLOWRIDE_API_URL and FLOWRIDE_API_KEY in Streamlit Secrets.")
    st.stop()


def call(path, params=None, timeout=90):
    r = requests.get(
        API_URL + path,
        params=params or {},
        headers={"X-API-Key": API_KEY},
        timeout=timeout,
    )
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(str(detail))
    return r.json()

# Backend health. V8.0.1 currently exposes status/version, not universe counts.
try:
    h = call("/health", timeout=20)
    st.info(f"Backend: **ONLINE** • {h.get('version', 'unknown')}")
except Exception:
    st.warning("Backend is waking up or unavailable. Try again in a moment.")

st.subheader("🔎 Search Stock")
q = st.text_input(
    "Search NSE/BSE symbol, company name or scrip code",
    placeholder="RELIANCE, TCS, PRICOL, 500325...",
)
ex = st.selectbox("Exchange", ["ALL", "NSE", "BSE"])

if st.button("🔍 SEARCH", type="primary") and q.strip():
    try:
        params = {"q": q.strip(), "limit": 100}
        # The private API accepts the query and returns exchange in each result.
        data = call("/search", params)
        if not isinstance(data, list):
            raise RuntimeError("Unexpected search response from backend")
        if ex != "ALL":
            data = [r for r in data if str(r.get("exchange", "")).upper() == ex]
        st.session_state.results = data
    except Exception as e:
        st.error(f"Search failed: {e}")

results = st.session_state.get("results", [])
if results:
    st.success(f"Found {len(results)} matching securities.")
    labels = [f"{r.get('symbol','')} — {r.get('name','')} ({r.get('exchange','')})" for r in results]
    idx = st.selectbox("Select stock", range(len(labels)), format_func=lambda i: labels[i])
    sel = results[idx]

    if st.button("📊 ANALYZE SELECTED STOCK", type="primary"):
        try:
            with st.spinner(f"Loading {sel['symbol']}..."):
                a = call("/analyze", {"exchange": sel["exchange"], "symbol": sel["symbol"]}, timeout=120)
            st.session_state.analysis = a
        except Exception as e:
            st.error(f"Analysis failed: {e}")

analysis = st.session_state.get("analysis")
if analysis:
    st.divider()
    st.subheader(f"📊 {analysis['symbol']} | {analysis['name']} ({analysis['exchange']})")

    flow = analysis.get("flowride", {})
    metrics = analysis.get("metrics", {})
    state = str(flow.get("state", "RIDE"))
    flow_score = float(flow.get("score", 0) or 0)
    icon = "🟢" if state == "BUY" else "🔴" if state == "EXIT" else "🔵"
    st.markdown(
        f"<div class='flow'>{icon} {state}<br><span style='font-size:15px'>Flow Score {flow_score:.0f}/100</span></div>",
        unsafe_allow_html=True,
    )

    c = st.columns(4)
    c[0].metric("Close", f"₹{metrics.get('price', 0):,.2f}")
    c[1].metric("Score", f"{metrics.get('score', 0):.0f}/100")
    c[2].metric("Signal", metrics.get("signal", "—"))
    rsi = metrics.get("rsi")
    c[3].metric("RSI", f"{float(rsi):.1f}" if rsi is not None else "—")

    c = st.columns(3)
    c[0].metric("Stop Loss", f"₹{metrics.get('stop', 0):,.2f}")
    c[1].metric("Target 1", f"₹{metrics.get('target1', 0):,.2f}")
    c[2].metric("Target 2", f"₹{metrics.get('target2', 0):,.2f}")

    st.caption(
        f"Latest data: {analysis.get('latest_date','—')} • Data is historical/delayed, not exchange real-time."
    )
    reasons = metrics.get("reasons") or []
    if reasons:
        st.write("**Positive factors:** " + " • ".join(reasons))

    # Simple non-candlestick price/flow chart.
    chart = analysis.get("chart", {})
    if chart.get("date") and chart.get("price"):
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=chart["date"], y=chart["price"], mode="lines", name="Price"))
        if chart.get("ema20"):
            fig.add_trace(go.Scatter(x=chart["date"], y=chart["ema20"], mode="lines", name="20 EMA", line=dict(dash="dot")))
        ride = chart.get("ride", [])
        buy = chart.get("buy", [])
        exit_ = chart.get("exit", [])
        if any(v is not None for v in ride):
            fig.add_trace(go.Scatter(x=chart["date"], y=ride, mode="lines", name="RIDE"))
        if any(v is not None for v in buy):
            fig.add_trace(go.Scatter(x=chart["date"], y=buy, mode="markers+text", name="BUY", text=["BUY" if v is not None else "" for v in buy], textposition="top center"))
        if any(v is not None for v in exit_):
            fig.add_trace(go.Scatter(x=chart["date"], y=exit_, mode="markers+text", name="EXIT", text=["EXIT" if v is not None else "" for v in exit_], textposition="bottom center"))
        fig.update_layout(height=480, xaxis_rangeslider_visible=False, hovermode="x unified", yaxis_title="Price (₹)")
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("🚀 Ranked Universe Scanner")
scan_ex = st.selectbox("Exchange for scan", ["NSE", "BSE"])
limit = st.number_input("Stocks to scan", min_value=10, max_value=300, value=25, step=5)

if st.button("🔄 RUN EOD SCAN", type="primary"):
    try:
        with st.spinner(f"Scanning {limit} {scan_ex} securities…"):
            data = call("/scan", {"exchange": scan_ex, "limit": int(limit)}, timeout=600)
        if not isinstance(data, list):
            raise RuntimeError("Unexpected scan response from backend")
        out = pd.DataFrame(data)
        st.success(f"Usable results: {len(out)}")
        if not out.empty:
            display_cols = [c for c in ["Symbol", "Company", "Exchange", "Close", "Score", "Signal", "FLOWRIDE", "Flow Score", "RSI", "ATR %"] if c in out.columns]
            st.dataframe(out[display_cols], use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Scan failed: {e}")

st.caption("FLOWRIDE is a rules-based technical market-analysis system. It is not personalized investment advice.")
