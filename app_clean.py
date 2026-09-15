"""FLOWRIDE clean main entrypoint.

Runs the existing app.py unchanged except for removing the legacy synchronous
Ranked Opportunity Scanner block embedded on the homepage. The supported
scanner is the separate pages/3_Async_EOD_Scanner.py page.
"""
from pathlib import Path

SOURCE = Path(__file__).with_name("app.py")
code = SOURCE.read_text(encoding="utf-8")

start_marker = 'st.divider()\nst.subheader("🚀 Ranked Opportunity Scanner")'
end_marker = 'st.divider()\nst.markdown("### About Stocks Rides")'

start = code.find(start_marker)
end = code.find(end_marker, start + 1) if start >= 0 else -1

if start < 0 or end < 0 or end <= start:
    raise RuntimeError(
        "Could not locate the legacy Ranked Opportunity Scanner block in app.py. "
        "No partial modification was applied."
    )

replacement = '''st.divider()\nst.info("🚀 EOD scanning has moved to the **Async EOD Scanner** page in the sidebar. The old blocking scanner was removed from the homepage.")\n\n'''
clean_code = code[:start] + replacement + code[end:]

exec(compile(clean_code, str(SOURCE), "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})
