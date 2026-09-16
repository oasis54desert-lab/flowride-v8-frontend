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
    st.error("Backend configuration is missing. Set FLOWRIDE_API_URL and FLOWRIDE_API_KEY in Streamlit Secrets.")
    st.stop()


def call(path, params=None, timeout=90):
    r = requests.get(API_URL + path, params=params or {}, headers={"X-API-Key": API_KEY, "Accept": "application/json"}, timeout=timeout)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(str(detail))
    return r.json()


st.title("🧭 FLOWRIDE Strategy Studio")
st.caption("Discover → Validate → Track → BUY → RIDE → EXIT")
st.info("V19 is an additive research/presentation layer. The frozen production BUY → RIDE → EXIT lifecycle is not changed by this page.")

try:
    h = requests.get(API_URL + "/health", timeout=20).json()
    st.success(f"Backend ONLINE • {h.get('version','unknown')} • Universe {int(h.get('total',0)):,} • NSE {int(h.get('nse',0)):,} • BSE {int(h.get('bse',0)):,}")
except Exception:
    st.warning("Backend is waking up or unavailable.")

STRATEGIES = [
    {
        "name": "FLOWRIDE RC1 Lifecycle",
        "layer": "Production candidate",
        "status": "FROZEN",
        "source": "V16 / V17",
        "purpose": "Disciplined entry, ride management and exit using the frozen candidate.",
        "metrics": "Completed trades • Win rate • Average/median net return • Profit factor • Strict profitable outperformance"
    },
    {
        "name": "Early Watch",
        "layer": "Discovery",
        "status": "RESEARCH",
        "source": "V4 → V15",
        "purpose": "Observe developing setups before strict lifecycle BUY without weakening production BUY.",
        "metrics": "Setup conversion • Winner capture • False-alert rate • Forward return"
    },
    {
        "name": "Discovery Quality / Ranking",
        "layer": "Ranking",
        "status": "RESEARCH",
        "source": "V9 → V12",
        "purpose": "Rank simultaneous candidates while keeping discovery separate from trade management.",
        "metrics": "Top-band precision • Recall • Trade conversion • OOS ranking stability"
    },
    {
        "name": "Winner Path",
        "layer": "Exit research",
        "status": "RESEARCH",
        "source": "V5 → V7",
        "purpose": "Study how proven winners develop and how much of their maximum favourable excursion is retained.",
        "metrics": "MFE • MAE • Profit capture • Exit reason • Winner retention"
    },
    {
        "name": "Portfolio Stress",
        "layer": "Portfolio validation",
        "status": "VALIDATION",
        "source": "V18",
        "purpose": "Test whether trade-level results survive capital, slot and transaction-cost constraints.",
        "metrics": "Total return • CAGR • Max drawdown • Profit factor • Exposure • Skipped entries • Winner concentration"
    },
]

names = [x["name"] for x in STRATEGIES]
selected_name = st.selectbox("Strategy Library", names)
s = next(x for x in STRATEGIES if x["name"] == selected_name)

c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown(f"### {s['name']}")
    st.write(s["purpose"])
with c2:
    st.metric("Layer", s["layer"])
with c3:
    st.metric("Status", s["status"])
st.caption(f"Evidence source: {s['source']}")
st.markdown("**Measured on:** " + s["metrics"])

st.divider()
st.subheader("📚 Strategy Library Overview")
st.dataframe(pd.DataFrame(STRATEGIES), use_container_width=True, hide_index=True)

st.divider()
st.subheader("🧪 Research Evidence")
st.caption("Run research from the existing FLOWRIDE research modules. Strategy Studio is deliberately read-oriented and does not mutate production thresholds.")

if selected_name == "FLOWRIDE RC1 Lifecycle":
    st.markdown("#### RC1 robustness — V17")
    job_id = st.text_input("Completed V17 job ID (optional)", key="studio_v17_job")
    if job_id and st.button("Load V17 evidence", use_container_width=True):
        try:
            raw = call("/v17_rc1_robustness_job/result", {"job_id": job_id}, timeout=120)
            st.session_state["studio_v17_result"] = raw
        except Exception as e:
            st.error(f"Could not load V17 result: {e}")
    raw = st.session_state.get("studio_v17_result")
    if raw:
        rows = raw.get("per_seed_trade_metrics", []) or raw.get("seed_results", []) or []
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        agg = raw.get("aggregate_robustness") or raw.get("aggregate")
        if agg:
            st.json(agg)
    else:
        st.info("Use a completed V17 job ID to surface robustness evidence here.")

elif selected_name == "Portfolio Stress":
    st.markdown("#### Portfolio stress — V18")
    st.write("V18 remains the portfolio-level reality check: trade-level edge and portfolio edge are treated as separate questions.")
    st.info("Run the existing V18 stress module in the main FLOWRIDE research interface, then compare cost, drawdown, allocation and winner-concentration results here as the dashboard evolves.")

elif selected_name == "Early Watch":
    st.markdown("#### Early Watch research")
    st.write("Use this layer to compare developing setups, confirmed setups and failed setups before considering any production-rule change.")

elif selected_name == "Discovery Quality / Ranking":
    st.markdown("#### Candidate ranking research")
    st.write("This layer studies which candidates deserve scarce attention or portfolio slots. It does not convert ranking into a proven portfolio-admission rule.")

elif selected_name == "Winner Path":
    st.markdown("#### Winner-path research")
    st.write("This layer focuses on preserving asymmetric winners while studying MFE, MAE, profit protection and exit behaviour.")

st.divider()
st.subheader("🔒 Methodology Guardrails")
st.markdown("""
- Production BUY / RIDE / EXIT rules remain frozen while research is evaluated.
- Historical, forward/paper and live evidence must remain separately labelled.
- Fresh out-of-sample validation is required before promoting a research change.
- Transaction costs, drawdown and portfolio constraints matter alongside win rate.
- Large-winner preservation matters because FLOWRIDE's historical return distribution is asymmetric.
""")
st.caption("FLOWRIDE V19 Strategy Studio • additive UI • research and decision-support only")
