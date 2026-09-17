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

def api(method,path,params=None,timeout=120):
    r=requests.request(method,API_URL+path,params=params or {},headers={"X-API-Key":API_KEY,"Accept":"application/json"},timeout=timeout)
    if r.status_code>=400:
        try: detail=r.json().get("detail",r.text)
        except Exception: detail=r.text
        raise RuntimeError(str(detail))
    return r.json()
def call(path,params=None,timeout=120): return api("GET",path,params,timeout)
def fmt(v,suffix="",dec=2):
    try:
        if v is None or pd.isna(v): return "—"
        return f"{float(v):,.{dec}f}{suffix}"
    except Exception: return str(v) if v not in (None,"") else "—"

st.markdown("""<style>
.block-container{padding-top:3.4rem;max-width:1250px}.fr-hero{padding:1rem 0 .8rem}.fr-title{font-size:2.35rem;font-weight:850;line-height:1.12;overflow:visible}.fr-sub{opacity:.7;margin-top:.55rem}.fr-card{border:1px solid rgba(128,128,128,.25);border-radius:16px;padding:1rem 1.05rem;min-height:155px;margin-bottom:.7rem}.fr-card h4{margin:.1rem 0 .35rem}.fr-tag{font-size:.78rem;opacity:.7}.fr-online{border:1px solid rgba(46,204,113,.35);border-radius:12px;padding:.7rem 1rem;margin:.5rem 0 1rem}@media(max-width:600px){.block-container{padding-top:4.2rem;padding-left:1rem;padding-right:1rem}.fr-hero{padding-top:.8rem}.fr-title{font-size:1.9rem;line-height:1.2}}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="fr-hero"><div class="fr-title">🧭 FLOWRIDE Strategy Studio</div><div class="fr-sub">Discover → Validate → Diagnose → Track → BUY → RIDE → EXIT</div></div>',unsafe_allow_html=True)
st.caption("V19.4 • Frozen validation + diagnostic research • Production BUY → RIDE → EXIT remains frozen")
try:
    h=requests.get(API_URL+"/health",timeout=20).json()
    st.markdown(f'<div class="fr-online">🟢 <b>Backend online</b> • Universe <b>{int(h.get("total",0)):,}</b> • NSE {int(h.get("nse",0)):,} • BSE {int(h.get("bse",0)):,}</div>',unsafe_allow_html=True)
except Exception: st.warning("Backend is waking up or unavailable.")

STRATEGIES=[
{"name":"FLOWRIDE RC1 Lifecycle","icon":"🌊","layer":"Production candidate","status":"FROZEN","source":"V16 / V17","purpose":"Frozen RC1 lifecycle validated across predeclared OOS seeds."},
{"name":"Accuracy Research","icon":"🔬","layer":"Diagnosis","status":"RESEARCH","source":"V17 diagnostic","purpose":"Compare winner-vs-loser entry conditions without changing production rules."},
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
st.caption("Metrics are read from completed backend research. Missing values are never estimated.")

if selected=="FLOWRIDE RC1 Lifecycle":
    jid=st.session_state.get("studio_v17_job_id")
    if not jid:
        st.info("No V17 run is attached to this browser session. Start the frozen validation below; FLOWRIDE will keep the job ID and load the result automatically.")
        if st.button("▶ Run frozen V17 validation",type="primary",use_container_width=True):
            try:
                started=api("POST","/v17_rc1_robustness_job/start",{"exchange":"NSE","limit":250,"period":"2y","dev_seed":357,"seed1":683,"seed2":797,"seed3":911,"total_cost_pct":0.25})
                st.session_state["studio_v17_job_id"]=started.get("job_id"); st.session_state.pop("studio_v17_result",None); st.rerun()
            except Exception as e: st.error(f"Could not start V17: {e}")
    else:
        try:
            status=call("/v17_rc1_robustness_job/status",{"job_id":jid},30); state=status.get("status","UNKNOWN"); pct=float(status.get("progress_pct",0) or 0)
            st.progress(max(0.0,min(1.0,pct/100.0)),text=f"V17 {state} • {pct:.0f}% • {status.get('message','')}")
            if state=="COMPLETED":
                if "studio_v17_result" not in st.session_state: st.session_state["studio_v17_result"]=call("/v17_rc1_robustness_job/result",{"job_id":jid},120)
            elif state in {"QUEUED","RUNNING"}:
                if st.button("↻ Refresh validation progress",use_container_width=True): st.rerun()
            elif state=="FAILED": st.error(status.get("error") or "V17 validation failed.")
        except Exception as e:
            st.warning(f"Saved V17 job is no longer available on the backend: {e}")
            if st.button("Clear saved job and start again",use_container_width=True):
                st.session_state.pop("studio_v17_job_id",None); st.session_state.pop("studio_v17_result",None); st.rerun()
    raw=st.session_state.get("studio_v17_result")
    if raw and raw.get("aggregate_robustness"):
        ag=raw["aggregate_robustness"]; m1,m2,m3,m4=st.columns(4)
        m1.metric("Completed trades",fmt(ag.get("TotalCompletedTrades"),dec=0)); m2.metric("Win rate",fmt(ag.get("WinRatePct"),"%")); m3.metric("Avg net return",fmt(ag.get("AvgNetReturnPct"),"%",3)); m4.metric("Profit factor",fmt(ag.get("ProfitFactor"),dec=3))
        m5,m6,m7,m8=st.columns(4); m5.metric("Seeds passed",f"{ag.get('SeedsPassed','—')} / {ag.get('SeedsTested','—')}"); m6.metric("Pass rate",fmt(ag.get("PassRatePct"),"%")); m7.metric("Strict outperform",fmt(ag.get("StrictProfitableOutperformancePct"),"%")); m8.metric("Avg MAE",fmt(ag.get("AvgMAE_Pct"),"%"))
        st.info(f"Robustness interpretation: {ag.get('RobustnessInterpretation','—')} • No seed selection • No threshold tuning")
        rows=pd.DataFrame(raw.get("per_seed_trade_metrics",[]))
        if not rows.empty:
            st.markdown("### Validation seeds"); st.dataframe(rows,use_container_width=True,hide_index=True)
            numeric=[col for col in ["AvgNetReturnPct","ProfitFactor","WinRatePct"] if col in rows.columns]
            if numeric and "ValidationSeed" in rows.columns: st.markdown("### Cross-seed stability"); st.bar_chart(rows.set_index("ValidationSeed")[numeric].apply(pd.to_numeric,errors="coerce"))
        with st.expander("Research definition & controls"):
            st.write(raw.get("frozen_candidate","")); st.write("Primary criteria:",raw.get("primary_criteria",[])); st.write(raw.get("benchmark_definition",""))
        if st.button("Run a new V17 validation",use_container_width=True): st.session_state.pop("studio_v17_job_id",None); st.session_state.pop("studio_v17_result",None); st.rerun()

elif selected=="Accuracy Research":
    st.warning("DIAGNOSTIC ONLY — this studies already-observed V17 seeds. It must not be used to tune production thresholds directly.")
    jid=st.session_state.get("studio_accuracy_job_id")
    if not jid:
        st.info("Run winner-vs-loser entry profiling. FLOWRIDE will rebuild the frozen DEV model, profile seeds 683/797/911 and compare entry conditions.")
        if st.button("🔬 Run Accuracy Research",type="primary",use_container_width=True):
            try:
                started=api("POST","/accuracy_research/start",{}); st.session_state["studio_accuracy_job_id"]=started.get("job_id"); st.session_state.pop("studio_accuracy_result",None); st.rerun()
            except Exception as e: st.error(f"Could not start accuracy research: {e}")
    else:
        try:
            status=call("/accuracy_research/status",{"job_id":jid},30); state=status.get("status","UNKNOWN"); pct=float(status.get("progress_pct",0) or 0)
            st.progress(max(0.0,min(1.0,pct/100.0)),text=f"Accuracy Research {state} • {pct:.0f}% • {status.get('message','')}")
            if state=="COMPLETED":
                if "studio_accuracy_result" not in st.session_state: st.session_state["studio_accuracy_result"]=call("/accuracy_research/result",{"job_id":jid},120)
            elif state in {"QUEUED","RUNNING"}:
                if st.button("↻ Refresh research progress",use_container_width=True): st.rerun()
            elif state=="FAILED": st.error(status.get("error") or "Accuracy research failed.")
        except Exception as e:
            st.warning(f"Saved accuracy job is no longer available: {e}")
            if st.button("Clear saved accuracy job",use_container_width=True): st.session_state.pop("studio_accuracy_job_id",None); st.session_state.pop("studio_accuracy_result",None); st.rerun()
    raw=st.session_state.get("studio_accuracy_result")
    if raw:
        hd=raw.get("headline",{}); m1,m2,m3,m4=st.columns(4)
        m1.metric("Trades profiled",fmt(hd.get("CompletedTradesProfiled"),dec=0)); m2.metric("Win rate",fmt(hd.get("WinRatePct"),"%")); m3.metric("Avg net return",fmt(hd.get("AvgNetReturnPct"),"%",3)); m4.metric("Profit factor",fmt(hd.get("ProfitFactor"),dec=3))
        st.markdown("### Cross-seed diagnostic summary"); seeds=pd.DataFrame(raw.get("seed_summary",[]));
        if not seeds.empty: st.dataframe(seeds,use_container_width=True,hide_index=True)
        feats=pd.DataFrame(raw.get("feature_diagnostics",[]))
        if not feats.empty:
            st.markdown("### Strongest winner-vs-loser differences")
            show=[c for c in ["Feature","WinnerN","LoserN","WinnerMean","LoserMean","StandardizedEffect","DirectionInWinners"] if c in feats.columns]
            st.dataframe(feats[show].head(12),use_container_width=True,hide_index=True)
            if "Feature" in feats.columns and "StandardizedEffect" in feats.columns:
                ch=feats.head(12).set_index("Feature")[["StandardizedEffect"]].apply(pd.to_numeric,errors="coerce"); st.bar_chart(ch)
        bands=pd.DataFrame(raw.get("band_diagnostics",[]))
        if not bands.empty:
            st.markdown("### Condition bands"); st.caption("Descriptive only. A strong historical band is not automatically a new threshold.")
            feature_options=sorted(bands["Feature"].dropna().astype(str).unique())
            chosen=st.selectbox("Inspect condition",feature_options,key="accuracy_band_feature")
            st.dataframe(bands[bands["Feature"].astype(str)==chosen],use_container_width=True,hide_index=True)
        rules=raw.get("research_rules",{})
        st.success("Next research step: identify ONE condition that is directionally stable across seeds, preregister it as a challenger, then test it on completely fresh untouched seeds.")
        with st.expander("Diagnostic guardrails"):
            st.write(raw.get("frozen_candidate","")); st.write(rules)

elif selected=="Portfolio Stress":
    st.info("V18 uses the completed V17 trades and reports Total Return, CAGR, portfolio drawdown, win rate, profit factor, exposure, transaction-cost stress and winner sensitivity. Values remain hidden until real V17 trade data is analyzed.")
    st.caption("V18 drawdown is realized-equity based; completed-trade inputs do not contain daily mark-to-market paths, so intratrade drawdown can be understated.")
elif selected=="Early Watch": st.info("Research-only layer. Measure conversion, false alerts and opportunity capture without changing production BUY.")
elif selected=="Discovery Quality / Ranking": st.info("Research-only ranking layer. Candidate rank prioritizes attention; it is not automatic production admission.")
else: st.info("Research-only winner-management layer. Evaluate MFE, MAE, giveback and holding behavior without weakening the frozen risk stop.")

st.divider(); st.subheader("🔒 Validation Guardrails")
st.markdown("Production BUY / RIDE / EXIT remains frozen • V17 baseline remains frozen • Predeclared OOS seeds 683, 797 and 911 are all reported • DEV seed 357 remains separate • No unfavorable seed may be discarded • Accuracy Research is diagnostic only • No production threshold tuning from observed V17 evidence • 0.25% round-trip cost is explicit • Missing metrics are never invented")
st.caption("FLOWRIDE V19.4 Strategy Studio • additive diagnostic frontend • V19.3 remains available by commit history")