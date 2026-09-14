from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')
start = 'st.divider()\nst.subheader("🧪 RC1 Stress & Portfolio Validation V18")'
end = 'st.divider()\nst.subheader("🧪 FLOWRIDE Strategy Validation")'
i = s.index(start)
j = s.index(end, i)

block = '''st.divider()
st.subheader("🧪 RC1 Stress & Portfolio Validation V18")
st.caption(
    "RC1 remains frozen. V18 adds portfolio-level stress testing only; it does not change "
    "discovery, ranking, Grace5, V5 Tight, risk-stop, BUY/RIDE/EXIT logic, or prior settings."
)

st.info(
    "The frozen V17 trades dataset is now stored server-side. No phone/browser CSV upload is required. "
    "Recommended starting test: ₹10,00,000 capital, 10 maximum simultaneous positions, "
    "10% position size, 0.25% base round-trip cost."
)

v18c1, v18c2, v18c3, v18c4 = st.columns(4)
with v18c1:
    v18_capital = st.number_input(
        "V18 Starting capital (₹)", min_value=10000.0, value=1000000.0,
        step=50000.0, key="v18_capital"
    )
with v18c2:
    v18_max_positions = st.number_input(
        "V18 Max simultaneous positions", min_value=1, max_value=100,
        value=10, step=1, key="v18_max_positions"
    )
with v18c3:
    v18_position_pct = st.number_input(
        "V18 Position size (% equity)", min_value=1.0, max_value=100.0,
        value=10.0, step=1.0, key="v18_position_pct"
    )
with v18c4:
    v18_base_cost = st.number_input(
        "V18 Base round-trip cost (%)", min_value=0.0, max_value=5.0,
        value=0.25, step=0.05, key="v18_base_cost"
    )

if st.button("🧪 Run V18 Stress & Portfolio Validation", use_container_width=True, key="run_v18"):
    try:
        _v18_params = {
            "starting_capital": float(v18_capital),
            "max_positions": int(v18_max_positions),
            "position_size_pct": float(v18_position_pct),
            "base_cost_pct": float(v18_base_cost),
        }
        with st.spinner("Running V18 portfolio and stress tests..."):
            _v18_resp = requests.post(
                API_URL.rstrip("/") + "/v18/analyze_default",
                params=_v18_params,
                headers={"X-API-Key": API_KEY, "Accept": "application/json"},
                timeout=300,
            )
        if _v18_resp.status_code != 200:
            st.error(f"V18 failed: HTTP {_v18_resp.status_code} — {_v18_resp.text}")
        else:
            _v18_res = _v18_resp.json()
            st.session_state["v18_last_result"] = _v18_res
            st.success("V18 completed using the frozen server-side V17 trades dataset.")
    except Exception as e:
        st.error(f"V18 request failed: {e}")

_v18_res = st.session_state.get("v18_last_result")
if _v18_res:
    st.markdown("#### Transaction-cost stress")
    st.dataframe(pd.DataFrame(_v18_res.get("cost_stress", [])), use_container_width=True, hide_index=True)
    st.markdown("#### Extreme-winner removal")
    st.dataframe(pd.DataFrame(_v18_res.get("extreme_winner_removal", [])), use_container_width=True, hide_index=True)
    st.markdown("#### Extreme-winner return caps")
    st.dataframe(pd.DataFrame(_v18_res.get("extreme_winner_caps", [])), use_container_width=True, hide_index=True)
    st.markdown("#### Winner concentration")
    st.dataframe(pd.DataFrame(_v18_res.get("winner_concentration", [])), use_container_width=True, hide_index=True)
    with st.expander("V18 methodology / limitations"):
        st.json(_v18_res.get("portfolio_rules", {}))
        for _note in _v18_res.get("notes", []):
            st.write("•", _note)
    try:
        _v18_csv = requests.post(
            API_URL.rstrip("/") + "/v18/export_default_csv",
            params={
                "starting_capital": float(v18_capital),
                "max_positions": int(v18_max_positions),
                "position_size_pct": float(v18_position_pct),
                "base_cost_pct": float(v18_base_cost),
            },
            headers={"X-API-Key": API_KEY, "Accept": "text/csv"},
            timeout=300,
        )
        if _v18_csv.status_code == 200:
            st.download_button(
                "⬇️ Download V18 Cost-Stress CSV",
                _v18_csv.content,
                file_name="flowride_v18_cost_stress.csv",
                mime="text/csv",
                use_container_width=True,
                key="v18_download_cost_csv",
            )
    except Exception as e:
        st.warning(f"V18 CSV export unavailable: {e}")

'''

p.write_text(s[:i] + block + s[j:], encoding='utf-8')
print('Patched app.py for V18 no-upload mode')
