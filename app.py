
import io
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="FLOWRIDE V18", layout="wide")
st.title("FLOWRIDE RC1 — Stress & Portfolio Validation V18")
st.caption("Frozen RC1 only. No signal/threshold/exit-rule optimization.")

API_BASE = st.text_input("Backend URL", value=st.session_state.get("v18_api_base","")).strip()
if API_BASE:
    st.session_state["v18_api_base"] = API_BASE

uploaded = st.file_uploader("Upload V17 trades CSV", type=["csv"])

c1,c2,c3,c4 = st.columns(4)
with c1:
    capital = st.number_input("Starting capital (₹)", min_value=10000.0, value=1000000.0, step=50000.0)
with c2:
    max_positions = st.number_input("Max simultaneous positions", min_value=1, max_value=100, value=10, step=1)
with c3:
    pos_pct = st.number_input("Position size (% equity)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
with c4:
    base_cost = st.number_input("Base round-trip cost (%)", min_value=0.0, max_value=5.0, value=0.25, step=0.05)

if st.button("Run V18 Stress & Portfolio Validation", use_container_width=True):
    if not API_BASE:
        st.error("Enter the backend URL.")
    elif uploaded is None:
        st.error("Upload the V17 trades CSV.")
    else:
        files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
        data = {
            "starting_capital": str(capital),
            "max_positions": str(int(max_positions)),
            "position_size_pct": str(pos_pct),
            "base_cost_pct": str(base_cost),
        }
        with st.spinner("Running frozen-RC1 portfolio stress tests..."):
            r = requests.post(API_BASE.rstrip("/") + "/v18/analyze", files=files, data=data, timeout=300)
        if r.status_code != 200:
            st.error(r.text)
        else:
            res = r.json()
            st.success("V18 completed — strategy rules remained frozen.")

            st.subheader("Transaction-cost stress")
            st.dataframe(pd.DataFrame(res["cost_stress"]), use_container_width=True, hide_index=True)

            st.subheader("Extreme-winner removal")
            st.dataframe(pd.DataFrame(res["extreme_winner_removal"]), use_container_width=True, hide_index=True)

            st.subheader("Extreme-winner return caps")
            st.dataframe(pd.DataFrame(res["extreme_winner_caps"]), use_container_width=True, hide_index=True)

            st.subheader("Winner concentration")
            st.dataframe(pd.DataFrame(res["winner_concentration"]), use_container_width=True, hide_index=True)

            with st.expander("Methodology / limitations"):
                st.json(res["portfolio_rules"])
                for note in res["notes"]:
                    st.write("•", note)

            # CSV export
            uploaded.seek(0)
            files2 = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
            r2 = requests.post(API_BASE.rstrip("/") + "/v18/export_csv", files=files2, data=data, timeout=300)
            if r2.status_code == 200:
                st.download_button(
                    "Download V18 cost-stress CSV",
                    r2.content,
                    file_name="flowride_v18_cost_stress.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
