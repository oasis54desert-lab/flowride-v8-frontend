import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="FLOWRIDE Strategy Studio", page_icon="🧭", layout="wide")

API_URL = os.getenv("FLOWRIDE_API_URL", "").rstrip("/")
API_KEY = os.getenv("FLOWRIDE_API_KEY", "")
try:
    API_URL = st.secrets.get("FLOWRIDE_API_URL", API_URL).rstrip("/")
    API_KEY = st.secrets.get("FLOWRIDE_API_KEY", API_KEY)
except Exception:
    pass

if not API_URL or not API_KEY:
    st.error("Backend configuration is missing.")
    st.stop()

def call(path, params=None, timeout=90):
    r = requests.get(API_URL + path, params=params or {}, headers={"X-API-Key": API_KEY, "Accept":"application/json"}, timeout=timeout)
    if r.status_code >= 400:
        try: detail = r.json().get("detail", r.text)
        except Exception: detail = r.text
        raise RuntimeError(str(detail))
    return r.json()

st.markdown("""
<style>
.block-container{padding-top:1.1rem;max-width:1250px}.fr-hero{padding:.5rem 0 1rem}.fr-title{font-size:2.35rem;font-weight:850;line-height:1.05}.fr-sub{opacity:.7;margin-top:.5rem}.fr-card{border:1px solid rgba(128,128,128,.25);border-radius:16px;padding:1rem 1.05rem;min-height:155px;margin-bottom:.7rem}.fr-card h4{margin:.1rem 0 .35rem}.fr-tag{font-size:.78rem;opacity:.7}.fr-online{border:1px solid rgba(46,204,113,.35);border-radius:12px;padding:.7rem 1rem;margin:.5rem 0 1rem}.fr-note{opacity:.7;font-size:.88rem}@media(max-width:600px){.fr-title{font-size:2rem}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="fr-hero"><div class="fr-title">🧭 FLOWRIDE Strategy Studio</div><div class="fr-sub">Discover → Validate → Track → BUY → RIDE → EXIT</div></div>', unsafe_allow_html=True)
st.caption("V19.1 • Research and performance workspace • Production BUY → RIDE → EXIT remains frozen")

try:
    h=requests.get(API_URL+"/health",timeout=20).json()
    st.markdown(f'<div class="fr-online">🟢 <b>Backend online</b> &nbsp;•&nbsp; Universe <b>{int(h.get("total",0)):,}</b> &nbsp;•&nbsp; NSE {int(h.get("nse",0)):,} &nbsp;•&nbsp; BSE {int(h.get("bse",0)):,}</div>',unsafe_allow_html=True)
except Exception:
    st.warning("Backend is waking up or unavailable.")

STRATEGIES=[
{"name":"FLOWRIDE RC1 Lifecycle","icon":"🌊","layer":"Production candidate","status":"FROZEN","source":"V16 / V17","purpose":"Disciplined entry, ride management and exit using the frozen candidate.","metrics":"Completed trades • Win rate • Average net return • Profit factor • Strict profitable outperformance"},
{"name":"Early Watch","icon":"👀","layer":"Discovery","status":"RESEARCH","source":"V4 → V15","purpose":"Observe developing setups before strict lifecycle BUY without weakening production BUY.","metrics":"Setup conversion • Winner capture • False-alert rate • Forward return"},
{"name":"Discovery Quality / Ranking","icon":"🏆","layer":"Ranking","status":"RESEARCH","source":"V9 → V12","purpose":"Rank simultaneous candidates while keeping discovery separate from trade management.","metrics":"Top-band precision • Recall • Trade conversion • OOS ranking stability"},
{"name":"Winner Path","icon":"🚀","layer":"Exit research","status":"RESEARCH","source":"V5 → V7","purpose":"Study how proven winners develop and how much favourable excursion is retained.","metrics":"MFE • MAE • Profit capture • Exit reason • Winner retention"},
{"name":"Portfolio Stress","icon":"🛡️","layer":"Portfolio validation","status":"VALIDATION","source":"V18","purpose":"Test whether trade-level results survive capital, slot and transaction-cost constraints.","metrics":"Total return • CAGR • Max drawdown • Profit factor • Exposure • Winner concentration"}]

st.subheader("Strategy Library")
cols=st.columns(3)
for i,x in enumerate(STRATEGIES):
    with cols[i%3]:
        st.markdown(f'<div class="fr-card"><div style="font-size:1.6rem">{x["icon"]}</div><h4>{x["name"]}</h4><div class="fr-tag">{x["layer"]} • {x["status"]}</div><p>{x["purpose"]}</p></div>',unsafe_allow_html=True)

names=[x["name"] for x in STRATEGIES]
selected_name=st.selectbox("Explore strategy",names,key="studio_strategy")
s=next(x for x in STRATEGIES if x["name"]==selected_name)
st.markdown(f"## {s['icon']} {s['name']}")
a,b,c=st.columns(3)
a.metric("Layer",s["layer"]); b.metric("Status",s["status"]); c.metric("Evidence",s["source"])
st.write(s["purpose"])
st.caption("Measured on: "+s["metrics"])

st.divider()
st.subheader("📊 Performance Evidence")
st.caption("Only measured results are shown. Blank metrics are not estimated or invented.")

if selected_name=="FLOWRIDE RC1 Lifecycle":
    job_id=st.text_input("Completed V17 robustness job ID",key="studio_v17_job",placeholder="Paste a completed V17 job ID")
    if job_id and st.button("Load robustness dashboard",type="primary",use_container_width=True):
        try: st.session_state["studio_v17_result"]=call("/v17_rc1_robustness_job/result",{"job_id":job_id},120)
        except Exception as e: st.error(f"Could not load V17 result: {e}")
    raw=st.session_state.get("studio_v17_result")
    if raw:
        rows=raw.get("per_seed_trade_metrics",[]) or raw.get("seed_results",[]) or []
        df=pd.DataFrame(rows)
        if not df.empty:
            def mean_col(*names):
                for n in names:
                    if n in df.columns: return pd.to_numeric(df[n],errors="coerce").mean()
                return None
            wr=mean_col("WinRatePct","WinRate"); ar=mean_col("AvgNetReturnPct","AverageNetReturnPct"); pf=mean_col("ProfitFactor")
            m1,m2,m3,m4=st.columns(4)
            m1.metric("Validation seeds",len(df)); m2.metric("Avg win rate","—" if pd.isna(wr) else f"{wr:.1f}%"); m3.metric("Avg net return","—" if pd.isna(ar) else f"{ar:.2f}%"); m4.metric("Profit factor","—" if pd.isna(pf) else f"{pf:.2f}")
            st.dataframe(df,use_container_width=True,hide_index=True)
        agg=raw.get("aggregate_robustness") or raw.get("aggregate")
        if agg:
            with st.expander("Aggregate robustness details"): st.json(agg)
    else: st.info("Load a completed V17 job to populate verified win-rate, return and robustness metrics.")
elif selected_name=="Portfolio Stress":
    st.info("V18 is the portfolio reality check. Next connection will surface CAGR, total return, max drawdown, cost sensitivity and the portfolio equity curve from a completed V18 run.")
elif selected_name=="Early Watch": st.info("Compare developing setups, confirmed setups and failed setups. Research remains separate from production BUY.")
elif selected_name=="Discovery Quality / Ranking": st.info("Evaluate which simultaneous candidates deserve attention or scarce portfolio slots without treating ranking as a proven admission rule.")
else: st.info("Study MFE, MAE, profit capture and exit behaviour to preserve asymmetric winners without weakening risk control.")

st.divider(); st.subheader("🔎 Research Filters")
f1,f2,f3=st.columns(3)
with f1: st.selectbox("Market",["NSE + BSE","NSE","BSE"],disabled=True)
with f2: st.selectbox("Evidence window",["Latest validated run","1Y","3Y","5Y"],disabled=True)
with f3: st.selectbox("Sort metric",["Validated return","Drawdown","Win rate","Profit factor"],disabled=True)
st.caption("Filters are staged for the next data-connected release; disabled here to avoid implying unsupported results.")

st.divider(); st.subheader("🔒 Validation Guardrails")
st.markdown("Production BUY / RIDE / EXIT stays frozen during research • Historical and forward evidence stay separately labelled • Fresh OOS validation precedes promotion • Costs, drawdown and portfolio constraints matter alongside win rate • Large-winner preservation remains explicit")
st.caption("FLOWRIDE V19.1 Strategy Studio • additive UI • no production threshold changes")