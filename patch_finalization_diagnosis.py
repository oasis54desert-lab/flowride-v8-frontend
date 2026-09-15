from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")

heading = 'st.subheader("🔬 Portfolio Failure Diagnosis — Finalization Research")'
if heading in s:
    print("Finalization diagnosis section already present")
    raise SystemExit(0)

marker = 'st.divider()\nst.subheader("🧪 FLOWRIDE Strategy Validation")'
idx = s.index(marker)

block = r'''st.divider()
st.subheader("🔬 Portfolio Failure Diagnosis — Finalization Research")
st.caption(
    "This is NOT a new strategy version. It diagnoses why V11-priority failed the V20B fresh-OOS test. "
    "RC1, V11, BUY/RIDE/EXIT, Grace5, V5 Tight, risk stop and portfolio rules remain frozen."
)

st.info(
    "The diagnosis reuses already-observed V20B seeds 1021, 1153 and 1297 only to explain the failure. "
    "These seeds are permanently excluded from future tuning."
)

if st.button("🔬 Run Portfolio Failure Diagnosis", use_container_width=True, key="run_finalization_diag"):
    try:
        start_diag = call_post("/finalization/portfolio_failure_diagnosis/start", timeout=60)
        jid_diag = str(start_diag.get("job_id", "") or "").strip()
        if not jid_diag:
            raise RuntimeError("Backend did not return a diagnosis job ID.")
        st.session_state["finalization_diag_job_id"] = jid_diag
        st.session_state.pop("finalization_diag_result", None)
        st.rerun()
    except Exception as e:
        st.error(f"Diagnosis start failed: {e}")

jid_diag = st.session_state.get("finalization_diag_job_id")
if jid_diag and "finalization_diag_result" not in st.session_state:
    try:
        js_diag = call(
            "/finalization/portfolio_failure_diagnosis/status",
            {"job_id": jid_diag},
            timeout=30,
        )
        status_diag = str((js_diag or {}).get("status", "")).upper()
        pct_diag = float((js_diag or {}).get("progress_pct", 0) or 0)
        msg_diag = str((js_diag or {}).get("message", status_diag or "Working"))
        st.progress(max(0, min(100, int(round(pct_diag)))))
        st.info(f"Finalization diagnosis: {msg_diag} • {pct_diag:.0f}%")

        if status_diag == "COMPLETED":
            rr_diag = call(
                "/finalization/portfolio_failure_diagnosis/result",
                {"job_id": jid_diag},
                timeout=180,
            )
            st.session_state["finalization_diag_result"] = rr_diag
            st.success("Portfolio Failure Diagnosis completed.")
            st.rerun()
        elif status_diag == "FAILED":
            st.error((js_diag or {}).get("error", "Diagnosis failed."))
        else:
            time.sleep(5)
            st.rerun()
    except Exception as e:
        st.warning(f"Diagnosis status unavailable: {e}")

_diag = st.session_state.get("finalization_diag_result")
if _diag:
    st.warning(
        "V11-priority remains REJECTED for promotion. This report explains the failure; it does not authorize tuning."
    )

    st.markdown("#### Selection displacement by fresh seed")
    st.dataframe(pd.DataFrame(_diag.get("seed_selection_summary", [])), use_container_width=True, hide_index=True)

    st.markdown("#### Policy-level trade characteristics")
    st.dataframe(pd.DataFrame(_diag.get("policy_metrics", [])), use_container_width=True, hide_index=True)

    st.markdown("#### What changed when V11-priority replaced First-Come trades")
    st.dataframe(pd.DataFrame(_diag.get("selection_subset_metrics", [])), use_container_width=True, hide_index=True)

    st.markdown("#### Exit-reason distribution")
    st.dataframe(pd.DataFrame(_diag.get("exit_reason_distribution", [])), use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Winners First-Come selected but V11-priority missed")
        st.dataframe(pd.DataFrame(_diag.get("missed_first_come_winners", [])), use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### Losers V11-priority added")
        st.dataframe(pd.DataFrame(_diag.get("added_v11_priority_losers", [])), use_container_width=True, hide_index=True)

    with st.expander("Diagnosis flags / finalization decision"):
        st.json(_diag.get("diagnosis_flags", {}))
        st.json(_diag.get("decision", {}))

    try:
        _diag_csv = call_bytes(
            "/finalization/portfolio_failure_diagnosis/csv",
            {"job_id": jid_diag},
            timeout=120,
        )
        st.download_button(
            "⬇️ Download Portfolio Failure Diagnosis CSV",
            _diag_csv,
            file_name="flowride_portfolio_failure_diagnosis.csv",
            mime="text/csv",
            use_container_width=True,
            key="finalization_diag_download",
        )
    except Exception as e:
        st.warning(f"Diagnosis CSV export unavailable: {e}")

'''

p.write_text(s[:idx] + block + s[idx:], encoding="utf-8")
print("Inserted finalization portfolio failure diagnosis section")
