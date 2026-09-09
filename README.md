# FLOWRIDE V9.1 Frontend

This is the separate Streamlit customer interface. It calls the private FastAPI backend through protected API requests.

## Streamlit secrets

Create `.streamlit/secrets.toml` from `.streamlit/secrets.toml.example`:

```toml
FLOWRIDE_API_URL = "https://YOUR-BACKEND-URL"
FLOWRIDE_API_KEY = "YOUR-SAME-BACKEND-API-KEY"
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The backend must be online before the frontend can perform analysis, validation or scanning.
