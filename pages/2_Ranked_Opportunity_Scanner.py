import os
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="FLOWRIDE Opportunity Scanner", page_icon="🚀", layout="wide")

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

HEADERS = {"X-API-Key": API_KEY, "Accept": "application/json"}


def _detail(r):
    try:
        d = r.json().get("detail", r.text)
        if isinstance(d, dict):
            return d.get("message") or str(d)
        return str(d)
    except Exception:
        return r.text


def get(path, params=None, timeout=30):
    try:
        r = requests.get(API_URL + path, params=params or {}, headers=HEADERS, timeout=timeout)
    except requests.Timeout as e:
        raise RuntimeError("Backend status request timed out. The server may be waking up; try again shortly.") from e
    except requests.RequestException as e:
        raise RuntimeError(f"Could not contact backend: {e}") from e
    if r.status_code >= 400:
        raise RuntimeError(_detail(r))
    return r.json()


def post(path, params=None, timeout=30):
    try:
        r = requests.post(API_URL + path, params=params or {}, headers=HEADERS, timeout=timeout)
    except requests.Timeout as e:
        raise RuntimeError("Backend start request timed out. Check backend health and try again.") from e
    except requests.RequestException as e:
        raise RuntimeError(f"Could not contact backend: {e}") from e
    if r.status_code >= 400:
        raise RuntimeError(_detail(r))
    return r.json()


st.title("🚀 Ranked Opportunity Scanner")
st.caption(
    "Async EOD scanner • V9 strategy logic unchanged • BUY → RIDE → EXIT lifecycle unchanged. "
    "Large scans run on the backend without holding one 10-minute HTTP request open."
)

try:
    health = requests.get(API_URL + "/health", timeout=15).json()
    st.success(
        f"Backend ONLINE • Universe {int(health.get('total', 0) or 0):,} "
        f"• NSE {int(health.get('nse', 0) or 0):,} • BSE {int(health.get('bse', 0) or 0):,}"
    )
except Exception:
    st.warning("Backend may be waking up. You can still try the scan after a moment.")

c1, c2, c3 = st.columns(3)
with c1:
    exchange = st.selectbox("Exchange for scan", ["NSE", "BSE"], key="async_scan_exchange")
with c2:
    stocks = st.select_slider(
        "Stocks to scan",
        options=[25, 50, 100, 200, 300, 500, 1000, 2000],
        value=300,
        key="async_scan_limit",
    )
with c3:
    sample_seed = st.number_input(
        "Sample seed",
        min_value=1,
        max_value=999999,
        value=89,
        step=1,
        help="Keep the same seed when comparing repeated scans.",
        key="async_scan_seed",
    )

force_refresh = st.checkbox(
    "Force fresh run (ignore today's same-setting cache)",
    value=False,
    help="Normally leave this off. Re-running the same settings on the same backend process can return the cached result immediately.",
)

st.info(
    "For large scans the page now starts a background job and checks short status requests. "
    "A 300-stock scan can therefore continue even when it takes longer than the old 600-second frontend timeout."
)

if st.button("🔄 RUN EOD SCAN", type="primary", use_container_width=True):
    try:
        start = post(
            "/scan_job/start",
            {
                "exchange": exchange,
                "limit": int(stocks),
                "sample_seed": int(sample_seed),
                "force_refresh": bool(force_refresh),
            },
            timeout=30,
        )
        job_id = str(start.get("job_id", "") or "").strip()
        if not job_id:
            raise RuntimeError("Backend did not return an EOD scan job ID.")

        st.session_state["eod_scan_job_id"] = job_id
        st.session_state.pop("eod_scan_result", None)
        st.session_state["eod_scan_params"] = {
            "exchange": exchange,
            "limit": int(stocks),
            "sample_seed": int(sample_seed),
        }

        progress = st.progress(int(start.get("percent", 2) or 2))
        status_box = st.empty()
        started_at = time.time()

        if start.get("cached"):
            status_box.success("Today's matching EOD scan is cached — loading results now.")
        else:
            status_box.info(start.get("message", "EOD scan started."))

        while True:
            status = get("/scan_job/status", {"job_id": job_id}, timeout=30)
            state = str(status.get("status", "") or "").upper()
            pct = float(status.get("percent", 0) or 0)
            progress.progress(max(0, min(100, int(round(pct)))))

            elapsed = int(time.time() - started_at)
            msg = status.get("message", state or "Working")
            if state in {"QUEUED", "RUNNING"}:
                status_box.info(f"{msg} • elapsed {elapsed // 60}m {elapsed % 60}s")
            elif state == "DONE":
                result = get("/scan_job/result", {"job_id": job_id}, timeout=120)
                st.session_state["eod_scan_result"] = result
                progress.progress(100)
                cache_note = " • cached result" if status.get("cached") else ""
                sec = status.get("elapsed_seconds")
                sec_text = f" • backend time {float(sec):.0f}s" if sec is not None else ""
                status_box.success(f"EOD scan completed{cache_note}{sec_text}.")
                break
            elif state == "FAILED":
                raise RuntimeError(status.get("error") or status.get("message") or "EOD scan failed.")
            else:
                status_box.info(f"Backend status: {state or 'UNKNOWN'}")

            # The job itself remains on the backend. This only prevents a single
            # Streamlit interaction from polling forever.
            if time.time() - started_at > 7200:
                raise RuntimeError(
                    "The backend scan is still running after 2 hours. The job was not cancelled; "
                    "check backend health before starting another scan."
                )
            time.sleep(5)

    except Exception as e:
        st.error(f"Scan failed: {e}")


raw = st.session_state.get("eod_scan_result")
if raw is not None:
    st.divider()
    st.subheader("📊 EOD Scan Results")

    if isinstance(raw, dict):
        rows = raw.get("results")
        if rows is None:
            # Backward compatibility with scan responses whose table may use a
            # different conventional key.
            for key in ("stocks", "data", "scan", "opportunities"):
                if isinstance(raw.get(key), list):
                    rows = raw.get(key)
                    break
        if rows is None and all(not isinstance(v, list) for v in raw.values()):
            st.json(raw)
            rows = []
    elif isinstance(raw, list):
        rows = raw
    else:
        rows = []

    df = pd.DataFrame(rows or [])
    if df.empty:
        st.warning("The backend completed the scan but returned no tabular opportunities for these settings.")
    else:
        # Put lifecycle columns first when present. No signal logic is altered.
        preferred = [
            "Symbol", "Name", "Exchange", "FLOWRIDE", "FlowState", "Lifecycle",
            "Signal", "Score", "FlowScore", "RSI", "RSI14", "ATR%", "ATRpct",
            "EarlyWatch", "OpportunityClass",
        ]
        ordered = [c for c in preferred if c in df.columns]
        ordered += [c for c in df.columns if c not in ordered]
        df = df[ordered]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download EOD Scan CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"flowride_scan_{st.session_state.get('eod_scan_params', {}).get('exchange', exchange)}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        lifecycle_col = next((c for c in ["FLOWRIDE", "FlowState", "Lifecycle", "State"] if c in df.columns), None)
        if lifecycle_col:
            counts = df[lifecycle_col].astype(str).str.upper().value_counts()
            cols = st.columns(4)
            for col, label in zip(cols, ["BUY", "RIDE", "EXIT", "FLAT"]):
                col.metric(label, int(counts.get(label, 0)))

st.caption(
    "Same-day cache is stored only in backend memory. A backend restart or redeploy clears it. "
    "Force Refresh should be used only when you intentionally want a new data fetch."
)
st.warning(
    "FLOWRIDE is a research and decision-support tool. EOD signals are not guaranteed outcomes; "
    "apply independent judgment and risk controls."
)
