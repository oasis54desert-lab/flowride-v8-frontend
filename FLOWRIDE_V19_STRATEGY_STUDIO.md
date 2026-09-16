# FLOWRIDE V19 Strategy Studio

Added 16 September 2026 as an additive Streamlit page.

## Preservation rule
The pre-V19 production state is preserved on branch `preserve-pre-v19-2026-09-16` in both the frontend and backend repositories.

V19 does **not** replace or rewrite the current main `app.py` or backend `api.py`. It adds `pages/Strategy_Studio.py` so the latest production runtime remains intact while Strategy Studio can evolve independently.

## Frozen core
Do not change the frozen V9 BUY gates, BUY → RIDE → EXIT lifecycle, RIDE Manager V3.1, RC1 logic, Early Watch production behavior, ranking, stops, Grace5 or profit-protection rules merely for UI work.

## Strategy Studio layers
- FLOWRIDE RC1 Lifecycle
- Early Watch
- Discovery Quality / Ranking
- Winner Path
- Portfolio Stress

## Development rule
Future Strategy Studio work should remain additive until separately validated. Research evidence must remain distinct from production signals and historical results must remain distinct from forward/paper/live evidence.
