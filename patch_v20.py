from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")

if 'st.subheader("🧪 V20 Portfolio Selection Robustness Gate")' in s:
    print("V20 frontend section already present")
    raise SystemExit(0)

marker = 'st.divider()\nst.subheader("🧪 FLOWRIDE Strategy Validation")'
idx = s.index(marker)

block = '''st.divider()
st.subheader("🧪 V20 Portfolio Selection Robustness Gate")
st.caption(
    "V20 does not change RC1, V11 ranking, or the V19 admission rule. It summarizes robustness of the already-observed V19 evidence and defines the next fresh-OOS gate."
)

st.warning(
    "Important: seeds 683, 797 and 911 were already observed in V19. V20 is therefore an exploratory robustness gate, NOT fresh out-of-sample proof and NOT a production-promotion test."
)

if st.button("🧪 Run V20 Robustness Gate", use_container_width=True, key="run_v20"):
    try:
        with st.spinner("Evaluating V20 portfolio-selection robustness..."):
            _v20_resp = requests.post(
                API_URL.rstrip("/") + "/v20/analyze_static",
                headers={"X-API-Key": API_KEY, "Accept": "application/json"},
                timeout=120,
            )
        if _v20_resp.status_code != 200:
            st.error(f"V20 failed: HTTP {_v20_resp.status_code} — {_v20_resp.text}")
        else:
            st.session_state["v20_last_result"] = _v20_resp.json()
            st.success("V20 robustness gate completed.")
    except Exception as e:
        st.error(f"V20 request failed: {e}")

_v20_res = st.session_state.get("v20_last_result")
if _v20_res:
    _gs = _v20_res.get("gate_summary", {})
    _status = _v20_res.get("status", "")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gates passed", f"{_gs.get('passed', 0)}/{_gs.get('total', 0)}")
    c2.metric("Seeds: return improved", f"{_gs.get('return_improved_seeds', 0)}/3")
    c3.metric("Seeds: PF improved", f"{_gs.get('pf_improved_seeds', 0)}/3")
    c4.metric("Worst return delta", f"{float(_gs.get('worst_return_delta_pp', 0)):.2f} pp")

    if _status == "EXPLORATORY_PASS_FRESH_OOS_REQUIRED":
        st.success("Exploratory V20 gate passes, but fresh OOS validation is still required before any promotion.")
    else:
        st.error("V20 found a robustness concern. Do not promote V19 selection logic.")

    st.markdown("#### Seed-level robustness")
    st.dataframe(pd.DataFrame(_v20_res.get("seed_robustness", [])), use_container_width=True, hide_index=True)

    st.markdown("#### Robustness gates")
    st.dataframe(pd.DataFrame(_v20_res.get("gates", [])), use_container_width=True, hide_index=True)

    _pooled = _v20_res.get("pooled_reference", {})
    if _pooled:
        st.markdown("#### Pooled reference")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("First-come return", f"{float(_pooled.get('first_come_total_return_pct', 0)):.2f}%")
        p2.metric("V11-priority return", f"{float(_pooled.get('v11_priority_total_return_pct', 0)):.2f}%")
        p3.metric("V11-priority PF", f"{float(_pooled.get('v11_priority_pf', 0)):.3f}")
        p4.metric("PF at 1.00% cost", f"{float(_pooled.get('cost_1pct_pf', 0)):.3f}")

    with st.expander("V20 next gate / fresh OOS criteria"):
        st.json(_v20_res.get("next_gate", {}))
        for _note in _v20_res.get("notes", []):
            st.write("•", _note)

    try:
        _v20_csv = requests.post(
            API_URL.rstrip("/") + "/v20/export_static_csv",
            headers={"X-API-Key": API_KEY, "Accept": "text/csv"},
            timeout=120,
        )
        if _v20_csv.status_code == 200:
            st.download_button(
                "⬇️ Download V20 Robustness CSV",
                _v20_csv.content,
                file_name="flowride_v20_portfolio_robustness.csv",
                mime="text/csv",
                use_container_width=True,
                key="v20_download_csv",
            )
    except Exception as e:
        st.warning(f"V20 CSV export unavailable: {e}")

'''

p.write_text(s[:idx] + block + s[idx:], encoding="utf-8")
print("Patched app.py with V20 robustness gate")
