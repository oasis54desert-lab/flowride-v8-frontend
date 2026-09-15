import os
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="FLOWRIDE Accuracy Research", page_icon="🔬", layout="wide")

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

HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}


def get_json(path, params=None, timeout=60):
    r = requests.get(API_URL + path, params=params or {}, headers=HEADERS, timeout=timeout)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(str(detail))
    return r.json()


def post_json(path, timeout=60):
    r = requests.post(API_URL + path, headers=HEADERS, timeout=timeout)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(str(detail))
    return r.json()


def get_bytes(path, params=None, timeout=120):
    h = {"X-API-Key": API_KEY, "Accept": "text/csv"}
    r = requests.get(API_URL + path, params=params or {}, headers=h, timeout=timeout)
    if r.status_code >= 400:
        raise RuntimeError(r.text)
    return r.content


st.title("🔬 FLOWRIDE Accuracy Improvement Research")
st.caption("Winner vs loser entry-profile diagnosis. This page does not change the production strategy.")

st.warning(
    "Research discipline: RC1, BUY → RIDE → EXIT, V11, Grace5, V5 Tight, risk stop and portfolio rules remain frozen. "
    "Seeds 683, 797 and 911 are already-observed research data and are used only to understand winner/loser conditions — never for fresh validation."
)

st.info(
    "The study compares winning and losing completed RC1 trades at signal time across trend structure, momentum, ADX/DI, ATR, persistent volume, "
    "EMA extension, recent returns, breakout position and candle structure. The objective is to remove false BUYs without destroying large winners."
)

if st.button("🔬 RUN WINNER vs LOSER RESEARCH", type="primary", use_container_width=True):
    try:
        js = post_json("/accuracy_research/start", timeout=60)
        jid = str(js.get("job_id", "") or "").strip()
        if not jid:
            raise RuntimeError("Backend did not return a job ID.")
        st.session_state["accuracy_job_id"] = jid
        st.session_state.pop("accuracy_result", None)
        st.rerun()
    except Exception as e:
        st.error(f"Could not start research: {e}")

jid = st.session_state.get("accuracy_job_id")
if jid and "accuracy_result" not in st.session_state:
    try:
        js = get_json("/accuracy_research/status", {"job_id": jid}, timeout=30)
        status = str(js.get("status", "")).upper()
        pct = float(js.get("progress_pct", 0) or 0)
        msg = str(js.get("message", status or "Working"))
        st.progress(max(0, min(100, int(round(pct)))))
        st.info(f"{msg} • {pct:.0f}%")
        if status == "COMPLETED":
            st.session_state["accuracy_result"] = get_json(
                "/accuracy_research/result", {"job_id": jid}, timeout=180
            )
            st.success("Winner-vs-loser research completed.")
            st.rerun()
        elif status == "FAILED":
            st.error(js.get("error", "Research failed."))
        else:
            time.sleep(5)
            st.rerun()
    except Exception as e:
        st.warning(f"Research status unavailable: {e}")

rr = st.session_state.get("accuracy_result")
if rr:
    h = rr.get("headline", {}) or {}
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Trades profiled", int(h.get("CompletedTradesProfiled", 0) or 0))
    c2.metric("Winners", int(h.get("Winners", 0) or 0))
    c3.metric("Losers", int(h.get("Losers", 0) or 0))
    c4.metric("Win rate", f"{float(h.get('WinRatePct', 0) or 0):.2f}%")
    c5.metric("Profit factor", f"{float(h.get('ProfitFactor', 0) or 0):.3f}")

    st.markdown("### Strongest winner-vs-loser differences")
    fd = pd.DataFrame(rr.get("feature_diagnostics", []))
    if not fd.empty:
        show_cols = [
            "Feature", "WinnerMean", "LoserMean", "WinnerMedian", "LoserMedian",
            "StandardizedEffect", "DirectionInWinners", "WinnerN", "LoserN"
        ]
        st.dataframe(fd[[c for c in show_cols if c in fd.columns]], use_container_width=True, hide_index=True)
    else:
        st.info("No feature diagnostic rows returned.")

    st.markdown("### Condition bands")
    bd = pd.DataFrame(rr.get("band_diagnostics", []))
    if not bd.empty:
        feature_options = list(dict.fromkeys(bd["Feature"].astype(str).tolist()))
        selected_feature = st.selectbox("Condition to inspect", feature_options)
        view = bd[bd["Feature"].astype(str) == selected_feature].copy()
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("No band diagnostics returned.")

    st.markdown("### Stability by previously observed seed")
    st.dataframe(pd.DataFrame(rr.get("seed_summary", [])), use_container_width=True, hide_index=True)

    with st.expander("Research rules / what happens next"):
        st.json(rr.get("research_rules", {}))
        st.json(rr.get("diagnostics", {}))

    try:
        fcsv = get_bytes("/accuracy_research/features_csv", {"job_id": jid})
        bcsv = get_bytes("/accuracy_research/bands_csv", {"job_id": jid})
        pcsv = get_bytes("/accuracy_research/profiles_csv", {"job_id": jid})
        d1, d2, d3 = st.columns(3)
        d1.download_button("⬇️ Feature diagnostics", fcsv, "flowride_winner_loser_feature_diagnostics.csv", "text/csv", use_container_width=True)
        d2.download_button("⬇️ Condition bands", bcsv, "flowride_winner_loser_band_diagnostics.csv", "text/csv", use_container_width=True)
        d3.download_button("⬇️ Entry profiles", pcsv, "flowride_winner_loser_entry_profiles.csv", "text/csv", use_container_width=True)
    except Exception as e:
        st.warning(f"CSV downloads unavailable: {e}")

    st.success(
        "Do not change thresholds from this page alone. First identify conditions that separate winners from losers consistently across the three observed seeds. "
        "Then preregister one accuracy challenger and test it on completely fresh seeds."
    )
