# FLOWRIDE Final Release Candidate — Frontend

Customer-facing Streamlit application for Stocks Rides PRO.

## Final product path

The normal UI now emphasizes the frozen production/core experience rather than the historical research-version stack:

- Search and analyze NSE/BSE securities
- FLOWRIDE `BUY -> RIDE -> EXIT` lifecycle
- Frozen RC1 core
- V11 retained for discovery/ranking context only
- Simple baseline portfolio allocation
- Archived research decisions shown only as supporting context
- Clear research/risk disclaimer

Pure V11-priority portfolio admission is not part of the final live path because it failed the V20B fresh out-of-sample promotion gate.

## Configuration

Configure Streamlit secrets with:

- `FLOWRIDE_API_URL`
- `FLOWRIDE_API_KEY`

The API key is used server-side by Streamlit and must not be exposed in browser code or committed to this public repository.

The final frontend can verify the private backend through `/release/status`.

## Release identity

`FLOWRIDE-FINAL-RELEASE-CANDIDATE-1`

Historical research code may remain in repository history for auditability, but failed experimental allocation rules are not presented as production logic.
