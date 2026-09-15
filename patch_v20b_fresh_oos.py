from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")

if 'st.subheader("🧪 V20B Fresh OOS Portfolio Selection")' in s:
    print("V20B section already present")
    raise SystemExit(0)

marker = 'st.divider()\nst.subheader("🧪 FLOWRIDE Strategy Validation")'
pos = s.index(marker)

block = r'''st.divider()
st.subheader("🧪 V20B Fresh OOS Portfolio Selection")
st.caption(
    "Fresh untouched validation of the frozen V19 V11-priority admission rule. "
    "RC1, V11 ranking, BUY/RIDE/EXIT, Grace5, V5 Tight and the -10% risk stop remain unchanged."
)

st.info(
    "Pre-registered before results: DEV seed 357; fresh seeds 1021, 1153 and 1297; NSE 250; 2y; "
    "₹10,00,000 portfolio; max 10 positions; 10% position size; 0.25% base round-trip cost. "
    "The fresh seeds and gates are locked in this test and cannot be changed from the UI."
)

with st.expander("V20B pre-registered pass criteria"):
    st.write("1. At least 2 of 3 fresh seeds: V11-priority total return > First-Come")
    st.write("2. At least 2 of 3 fresh seeds: V11-priority portfolio PF > First-Come")
    st.write("3. Pooled V11-priority PF > 1.00 at 0.50% round-trip cost")
    st.write("4. No fresh seed loses more than 10 percentage points versus First-Come")
    st.write("5. No fresh seed max drawdown worsens by more than 5 percentage points")
    st.caption("Promotion review requires a full 5/5 pass. No tuning is allowed from these fresh results.")

if st.button("🧪 Run V20B Fresh OOS Validation", use_container_width=True, key="run_v20b"):
    try:
        start20b = call_post("/v20b_fresh_oos_job/start", timeout=60)
        jid20b = str(start20b.get("job_id", "") or "").strip()
        if not jid20b:
            raise RuntimeError("Backend did not return a V20B job ID.")
        st.session_state["v20b_job_id"] = jid20b
        st.session_state.pop("v20b_last_result", None)
        st.rerun()
    except Exception as e:
        st.error(f"V20B start failed: {e}")

jid20b = st.session_state.get("v20b_job_id")
if jid20b and "v20b_last_result" not in st.session_state:
    try:
        js20b = call("/v20b_fresh_oos_job/status", {"job_id": jid20b}, timeout=30)
        status20b = str((js20b or {}).get("status", "")).upper()
        pct20b = float((js20b or {}).get("progress_pct", 0) or 0)
        msg20b = str((js20b or {}).get("message", status20b or "Working"))
        st.progress(max(0, min(100, int(round(pct20b)))))
        st.info(f"V20B: {msg20b} • {pct20b:.0f}%")

        if status20b == "COMPLETED":
            rr20b = call("/v20b_fresh_oos_job/result", {"job_id": jid20b}, timeout=180)
            st.session_state["v20b_last_result"] = rr20b
            st.success("V20B fresh OOS validation completed.")
            st.rerun()
        elif status20b == "FAILED":
            st.error((js20b or {}).get("error", "V20B failed."))
        else:
            time.sleep(5)
            st.rerun()
    except Exception as e:
        st.warning(f"V20B status unavailable: {e}")

_v20b = st.session_state.get("v20b_last_result")
if _v20b:
    _gs20b = _v20b.get("gate_summary", {})
    _st20b = _v20b.get("status", "")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fresh gates passed", f"{_gs20b.get('passed', 0)}/{_gs20b.get('total', 0)}")
    c2.metric("Return improved seeds", f"{_gs20b.get('return_improved_seeds', 0)}/3")
    c3.metric("PF improved seeds", f"{_gs20b.get('pf_improved_seeds', 0)}/3")
    _pf050 = _gs20b.get("pooled_v11_priority_pf_at_050_cost")
    c4.metric("Pooled PF @ 0.50%", f"{float(_pf050):.3f}" if _pf050 is not None else "—")

    if _st20b == "FRESH_OOS_PASS":
        st.success(
            "V20B FRESH OOS PASS: all pre-registered gates passed. This supports promotion review of the "
            "V11-priority portfolio admission rule, but daily mark-to-market and execution/liquidity validation are still required before real-capital use."
        )
    else:
        st.error(
            "V20B FRESH OOS FAIL: at least one pre-registered gate failed. Do not promote or tune the V11-priority rule from these fresh results."
        )

    st.markdown("#### Fresh-seed First-Come vs V11-priority")
    st.dataframe(pd.DataFrame(_v20b.get("fresh_seed_comparison", [])), use_container_width=True, hide_index=True)

    st.markdown("#### Pre-registered fresh-OOS gates")
    st.dataframe(pd.DataFrame(_v20b.get("gates", [])), use_container_width=True, hide_index=True)

    with st.expander("V20B decision / methodology"):
        st.json(_v20b.get("decision", {}))
        st.json(_v20b.get("portfolio_rules", {}))
        st.json(_v20b.get("diagnostics", {}))

    try:
        _v20b_csv = call_bytes("/v20b_fresh_oos_csv", {"job_id": jid20b}, timeout=120)
        st.download_button(
            "⬇️ Download V20B Fresh OOS CSV",
            _v20b_csv,
            file_name="flowride_v20b_fresh_oos_portfolio_selection.csv",
            mime="text/csv",
            use_container_width=True,
            key="v20b_download_csv",
        )
    except Exception as e:
        st.warning(f"V20B CSV export unavailable: {e}")

'''

p.write_text(s[:pos] + block + s[pos:], encoding="utf-8")
print("Inserted V20B fresh OOS section into app.py")
