# AIMN API

FastAPI control plane for media networks and channel workspaces.

## Local setup

```bash
cd apps/api
python -m venv .venv
# Activate the environment, then:
python -m pip install -e ".[dev]"
export AIMN_ADMIN_API_KEY="replace-with-a-long-random-local-key"
alembic upgrade head
uvicorn aimn_api.main:app --reload --app-dir src
```

For PostgreSQL install `.[dev,postgres]` and set `DATABASE_URL`, e.g. `postgresql+psycopg://aimn:YOUR_PASSWORD@localhost:5432/aimn`.

## API routes

- GET /health/live and /health/ready
- POST /api/v1/networks; GET /api/v1/networks and /api/v1/networks/{network_id}
- POST /api/v1/networks/{network_id}/channels
- GET /api/v1/networks/{network_id}/channels and /{channel_id}
- PATCH /api/v1/networks/{network_id}/channels/{channel_id}

All management routes require X-AIMN-API-Key. If AIMN_ADMIN_API_KEY is unset, the API fails closed with HTTP 503. This is a temporary single-operator bootstrap guard, not the final user authentication/RBAC implementation.

The API stores only a credential reference. OAuth tokens and client secrets are not accepted or returned by channel endpoints. Google OAuth connection and encrypted credential storage will be implemented separately.
