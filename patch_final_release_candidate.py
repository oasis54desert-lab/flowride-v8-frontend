from pathlib import Path
import re

p = Path("app.py")
s = p.read_text(encoding="utf-8")

# Present the app as a stable final release candidate rather than a research-version stack.
s = re.sub(
    r'^APP_VERSION\s*=\s*"[^"]*"',
    'APP_VERSION = "FLOWRIDE-FINAL-RELEASE-CANDIDATE-1"',
    s,
    count=1,
    flags=re.MULTILINE,
)

start = 'st.divider()\nst.subheader("⚡ Dynamic Winner Manager V7.2 ASYNC")'
end = 'st.divider()\nst.subheader("🧪 FLOWRIDE Strategy Validation")'

if start not in s:
    raise SystemExit("Final-release start marker not found")
if end not in s:
    raise SystemExit("Final-release end marker not found")

i = s.index(start)
j = s.index(end, i)

block = '''st.divider()
st.subheader("✅ FLOWRIDE Final Release Candidate")
st.caption(
    "Stable product path. The production core is frozen; failed experimental portfolio allocators are archived and are not part of the live decision path."
)

st.success(
    "FINAL RELEASE CANDIDATE • BUY → RIDE → EXIT core frozen • RC1 frozen • "
    "V11 retained for discovery/ranking context only • pure V11-priority portfolio admission rejected after fresh OOS validation."
)

r1, r2, r3, r4 = st.columns(4)
r1.metric("Lifecycle", "BUY → RIDE → EXIT")
r2.metric("Core", "RC1 FROZEN")
r3.metric("Ranking", "V11 DISCOVERY")
r4.metric("Portfolio", "SIMPLE BASELINE")

with st.expander("Research decisions archived", expanded=False):
    st.write("• V18 showed that realistic portfolio constraints can materially change trade-level results.")
    st.write("• V19/V20 found a promising V11-priority allocation effect on already-observed samples.")
    st.write("• V20B fresh OOS failed the pre-registered promotion gates, so pure V11-priority admission was rejected.")
    st.write("• Finalization diagnosis showed that higher V11 probability did not reliably improve marginal portfolio-slot outcomes.")
    st.write("• Seeds already used in V20B are not used to retune the rejected rule.")

if st.button("🔒 Check Final Release Status", use_container_width=True, key="final_release_status"):
    try:
        _release = call("/release/status", timeout=30)
        st.session_state["final_release_status_data"] = _release
        st.success("Final Release Candidate backend status confirmed.")
    except Exception as e:
        st.error(f"Release status check failed: {e}")

_release = st.session_state.get("final_release_status_data")
if _release:
    with st.expander("Release status details"):
        st.json(_release)

st.warning(
    "FLOWRIDE is a research and decision-support tool. Market outcomes are uncertain; signals, backtests and rankings do not guarantee future returns. "
    "Use independent judgment and appropriate risk controls."
)

'''

s = s[:i] + block + s[j:]
p.write_text(s, encoding="utf-8")
print("Patched app.py to FLOWRIDE Final Release Candidate UI")
