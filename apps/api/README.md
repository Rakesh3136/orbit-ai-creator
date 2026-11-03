# AIMN API

Minimal FastAPI control-plane skeleton.

## Local setup

```bash
cd apps/api
python -m venv .venv
# Activate the virtual environment, then:
python -m pip install -e ".[dev]"
uvicorn aimn_api.main:app --reload --app-dir src
```

OpenAPI docs are available at http://127.0.0.1:8000/docs.

## Current endpoints

- `GET /health/live` — process liveness.
- `GET /api/v1/system` — API identity and current development stage.

Database, authentication, channel CRUD, agent runtime, and CEO chat are intentionally not represented as working until their implementations and tests are added.
