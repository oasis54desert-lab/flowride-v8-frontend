import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="FLOWRIDE Strategy Studio", page_icon="🧭", layout="wide")
API_URL=os.getenv("FLOWRIDE_API_URL","").rstrip("/"); API_KEY=os.getenv("FLOWRIDE_API_KEY","")
try:
    API_URL=st.secrets.get("FLOWRIDE_API_URL",API_URL).rstrip("/"); API_KEY=st.secrets.get("FLOWRIDE_API_KEY",API_KEY)
except Exception: pass
if not API_URL or not API_KEY:
    st.error("Backend configuration is missing."); st.stop()

def call(path,params=None,timeout=120):
    r=requests.get(API_URL+path,params=params or {},headers={"X-API-Key":API_KEY,"Accept":"application/json"},timeout=timeout)
    if r.status_code>=400:
        try: detail=r.json().get("detail",r.text)
        except Exception: detail=r.text
        raise RuntimeError(str(detail))
    return r.json()

def fmt(v,suffix="",dec=2):
    try:
        if v is None or pd.isna(v): return "—"
        return f"{float(v):,.{dec}f}{suffix}"
    except Exception: return str(v) if v not in (None,"") else "—"

st.markdown("""<style>
.block-container{padding-top:2.8rem;max-width:1250px}.fr-hero{padding:1rem 0 .8rem}.fr-title{font-size:2.35rem;font-weight:850;line-height:1.12;overflow:visible}.fr-sub{opacity:.7;margin-top:.55rem}.fr-card{border:1px solid rgba(128,128,128,.25);border-radius:16px;padding:1rem 1.05rem;min-height:155px;margin-bottom:.7rem}.fr-card h4{margin:.1rem 0 .35rem}.fr-tag{font-size:.78rem;opacity:.7}.fr-online{border:1px solid rgba(46,204,113,.35);border-radius:12px;padding:.7rem 1rem;margin:.5rem 0 1rem}@media(max-width:600px){.block-container{padding-top:3.4rem;padding-left:1rem;padding-right:1rem}.fr-hero{padding-top:.8rem}.fr-title{font-size:1.9rem;line-height:1.2}}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="fr-hero"><div class="fr-title">🧭 FLOWRIDE Strategy Studio</div><div class="fr-sub">Discover → Validate → Track → BUY → RIDE → EXIT</div></div>',unsafe_allow_html=True)
st.caption("V19.2 • Verified research evidence • Production BUY → RIDE → EXIT remains frozen")
try:
    h=requests.get(API_URL+"/health",timeout=20).json()
    st.markdown(f'<div class="fr-online">🟢 <b>Backend online</b> • Universe <b>{int(h.get("total",0)):,}</b> • NSE {int(h.get("nse",0)):,} • BSE {int(h.get("bse",0)):,}</div>',unsafe_allow_html=True)
except Exception: st.warning("Backend is waking up or unavailable.")

STRATEGIES=[
{"name":"FLOWRIDE RC1 Lifecycle","icon":"🌊","layer":"Production candidate","status":"FROZEN","source":"V16 / V17","purpose":"Frozen RC1 lifecycle validated across predeclared OOS seeds."},
{"name":"Early Watch","icon":"👀","layer":"Discovery","status":"RESEARCH","source":"V4 → V15","purpose":"Observe developing setups before strict lifecycle BUY."},
{"name":"Discovery Quality / Ranking","icon":"🏆","layer":"Ranking","status":"RESEARCH","source":"V9 → V12","purpose":"Rank simultaneous candidates separately from trade management."},
{"name":"Winner Path","icon":"🚀","layer":"Exit research","status":"RESEARCH","source":"V5 → V7","purpose":"Study winner development, MFE, MAE and profit capture."},
{"name":"Portfolio Stress","icon":"🛡️","layer":"Portfolio validation","status":"VALIDATION","source":"V18","purpose":"Test capital, slot, transaction-cost and winner-concentration effects."}]
st.subheader("Strategy Library")
cols=st.columns(3)
for i,x in enumerate(STRATEGIES):
    with cols[i%3]: st.markdown(f'<div class="fr-card"><div style="font-size:1.6rem">{x["icon"]}</div><h4>{x["name"]}</h4><div class="fr-tag">{x["layer"]} • {x["status"]}</div><p>{x["purpose"]}</p></div>',unsafe_allow_html=True)
selected=st.selectbox("Explore strategy",[x["name"] for x in STRATEGIES],key="studio_strategy")
s=next(x for x in STRATEGIES if x["name"]==selected)
st.markdown(f"## {s['icon']} {s['name']}")
a,b,c=st.columns(3); a.metric("Layer",s["layer"]); b.metric("Status",s["status"]); c.metric("Evidence",s["source"])
st.write(s["purpose"])
st.divider(); st.subheader("📊 Verified Performance Evidence")
st.caption("Metrics below are read from completed backend research. FLOWRIDE does not estimate missing values.")

if selected=="FLOWRIDE RC1 Lifecycle":
    job_id=st.text_input("Completed V17 robustness job ID",key="studio_v17_job",placeholder="Paste completed V17 job ID")
    if st.button("Load V17 evidence",type="primary",use_container_width=True,disabled=not bool(job_id)):
        try:
            raw=call("/v17_rc1_robustness_job/result",{"job_id":job_id})
            if raw.get("status") and raw.get("status")!="COMPLETED": st.warning(f"Job {raw.get('status')}: {raw.get('message','')}")
            else: st.session_state["studio_v17_result"]=raw
        except Exception as e: st.error(f"Could not load V17 result: {e}")
    raw=st.session_state.get("studio_v17_result")
    if raw and raw.get("aggregate_robustness"):
        ag=raw["aggregate_robustness"]
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Completed trades",fmt(ag.get("TotalCompletedTrades"),dec=0)); m2.metric("Win rate",fmt(ag.get("WinRatePct"),"%")); m3.metric("Avg net return",fmt(ag.get("AvgNetReturnPct"),"%",3)); m4.metric("Profit factor",fmt(ag.get("ProfitFactor"),dec=3))
        m5,m6,m7,m8=st.columns(4)
        m5.metric("Seeds passed",f"{ag.get('SeedsPassed','—')} / {ag.get('SeedsTested','—')}"); m6.metric("Pass rate",fmt(ag.get("PassRatePct"),"%")); m7.metric("Strict outperform",fmt(ag.get("StrictProfitableOutperformancePct"),"%")); m8.metric("Avg MAE",fmt(ag.get("AvgMAE_Pct"),"%"))
        st.info(f"Robustness interpretation: {ag.get('RobustnessInterpretation','—')} • No seed selection • No threshold tuning")
        rows=pd.DataFrame(raw.get("per_seed_trade_metrics",[]))
        if not rows.empty:
            wanted=[x for x in ["ValidationSeed","Completed Trades","Win Rate %","Avg Net Return %","Median Net Return %","Profit Factor","Avg MFE %","Avg MAE %","Verdict"] if x in rows.columns]
            st.markdown("### Validation seeds"); st.dataframe(rows[wanted] if wanted else rows,use_container_width=True,hide_index=True)
            chart_cols=[x for x in ["Avg Net Return %","Profit Factor","Win Rate %"] if x in rows.columns]
            if chart_cols and "ValidationSeed" in rows.columns:
                chart=rows.set_index("ValidationSeed")[chart_cols].apply(pd.to_numeric,errors="coerce")
                st.markdown("### Cross-seed stability"); st.bar_chart(chart)
        with st.expander("Research definition & controls"):
            st.write(raw.get("frozen_candidate","")); st.write("Primary criteria:",raw.get("primary_criteria",[])); st.write(raw.get("benchmark_definition",""))
    else: st.info("Paste a completed V17 job ID to display genuine pooled and per-seed results.")
elif selected=="Portfolio Stress":
    st.info("V18 is verified in the backend and accepts a V17 completed-trades CSV. Its real outputs include Total Return, CAGR, portfolio drawdown, win rate, profit factor, exposure, cost stress and winner sensitivity. We will not show values until a V17 trade file is analyzed.")
    st.caption("Important: V18 drawdown is realized-equity based because the completed-trade file does not contain daily mark-to-market paths; intratrade drawdown can therefore be understated.")
elif selected=="Early Watch": st.info("Research-only layer. Use its forward setup metrics to measure conversion, false alerts and opportunity capture; it does not change production BUY.")
elif selected=="Discovery Quality / Ranking": st.info("Research-only ranking layer. Candidate rank is evidence for prioritization, not automatic admission into production.")
else: st.info("Research-only winner-management layer. Evaluate MFE, MAE, giveback and holding behavior without weakening the frozen risk stop.")

st.divider(); st.subheader("🔒 Validation Guardrails")
st.markdown("Production BUY / RIDE / EXIT remains frozen • All predeclared validation seeds are reported • No unfavorable seed may be discarded • No threshold tuning from V17 evidence • Transaction costs and portfolio constraints remain explicit • Missing metrics are never invented")
st.caption("FLOWRIDE V19.2 Strategy Studio • additive frontend only • V19.1 preserved on preserve-v19.1-2026-09-16")