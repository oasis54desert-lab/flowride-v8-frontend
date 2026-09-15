from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')

v19_start = 'st.subheader("🧪 V19 Portfolio Selection Research")'
next_marker = 'st.divider()\nst.subheader("🧪 FLOWRIDE Strategy Validation")'

block = '''st.divider()
st.subheader("🧪 V19 Portfolio Selection Research")
st.caption(
    "RC1 remains frozen. V19 tests only which eligible trades receive limited portfolio slots. "
    "No BUY/RIDE/EXIT, Grace5, V5 Tight, risk-stop, ranking model, or entry/exit rule is changed."
)

st.info(
    "V19 compares the V18 first-come portfolio against a frozen V11-priority admission rule: "
    "on each entry date, exits happen first, then same-day candidates are ranked by V11Probability "
    "and the highest-ranked candidates fill the available slots. Existing open positions are never replaced."
)

if st.button("🧪 Run V19 Portfolio Selection Research", use_container_width=True, key="run_v19"):
    try:
        with st.spinner("Running V19 portfolio-selection comparison..."):
            _v19_resp = requests.post(
                API_URL.rstrip("/") + "/v19/analyze_static",
                headers={"X-API-Key": API_KEY, "Accept": "application/json"},
                timeout=300,
            )
        if _v19_resp.status_code != 200:
            st.error(f"V19 failed: HTTP {_v19_resp.status_code} — {_v19_resp.text}")
        else:
            st.session_state["v19_last_result"] = _v19_resp.json()
            st.success("V19 portfolio-selection research completed.")
    except Exception as e:
        st.error(f"V19 request failed: {e}")

_v19_res = st.session_state.get("v19_last_result")
if _v19_res:
    _decision = _v19_res.get("decision", {})
    st.markdown("#### Pooled V18 baseline vs V11-priority selection")
    _pooled = pd.DataFrame(_v19_res.get("pooled_comparison", []))
    st.dataframe(_pooled, use_container_width=True, hide_index=True)

    if len(_pooled) >= 2:
        try:
            _base = _pooled[_pooled["SelectionPolicy"] == "FIRST_COME"].iloc[0]
            _prio = _pooled[_pooled["SelectionPolicy"] == "V11_PRIORITY"].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("V18 First-come return", f"{float(_base['TotalReturnPct']):.2f}%")
            c2.metric("V19 V11-priority return", f"{float(_prio['TotalReturnPct']):.2f}%")
            c3.metric("V19 Profit Factor", f"{float(_prio['PortfolioProfitFactor']):.3f}")
            c4.metric("V19 Max Drawdown", f"{float(_prio['MaxPortfolioDrawdownPct']):.2f}%")
        except Exception:
            pass

    st.markdown("#### Per-seed robustness")
    st.dataframe(pd.DataFrame(_v19_res.get("per_seed_comparison", [])), use_container_width=True, hide_index=True)

    st.markdown("#### V11-priority transaction-cost stress")
    st.dataframe(pd.DataFrame(_v19_res.get("v11_priority_cost_stress", [])), use_container_width=True, hide_index=True)

    _status = _decision.get("status", "")
    if _status == "RESEARCH_CHALLENGER_ONLY":
        st.warning(
            "V19 is a research challenger only. The pooled result improves strongly, but seed 683 worsens. "
            "Do not promote this allocation rule until it passes fresh untouched validation."
        )
    if _decision:
        with st.expander("V19 decision / next gate"):
            st.json(_decision)
    with st.expander("V19 methodology / limitations"):
        st.json(_v19_res.get("portfolio_rules", {}))
        for _note in _v19_res.get("notes", []):
            st.write("•", _note)

    try:
        _v19_csv = requests.post(
            API_URL.rstrip("/") + "/v19/export_static_csv",
            headers={"X-API-Key": API_KEY, "Accept": "text/csv"},
            timeout=300,
        )
        if _v19_csv.status_code == 200:
            st.download_button(
                "⬇️ Download V19 Portfolio-Selection CSV",
                _v19_csv.content,
                file_name="flowride_v19_portfolio_selection.csv",
                mime="text/csv",
                use_container_width=True,
                key="v19_download_csv",
            )
    except Exception as e:
        st.warning(f"V19 CSV export unavailable: {e}")

'''

if v19_start in s:
    i = s.index('st.divider()\n' + v19_start)
    j = s.index(next_marker, i)
    s = s[:i] + block + s[j:]
else:
    j = s.index(next_marker)
    s = s[:j] + block + s[j:]

p.write_text(s, encoding='utf-8')
print('Patched app.py with V19 portfolio-selection research')
