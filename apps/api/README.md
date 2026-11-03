# AIMN API

FastAPI control plane for the Autonomous AI Media Network.

## Local development

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn aimn_api.main:app --reload --app-dir src
```

Configure `DATABASE_URL` and a long random `AIMN_ADMIN_API_KEY`. Management routes fail closed when the key is missing. This API-key guard is a temporary single-operator bootstrap control, not final owner identity or role-based access control.

## Current control-plane endpoints

- `GET /health/live`, `GET /health/ready`
- `GET /api/v1/system`
- `GET/POST /api/v1/networks`
- `GET /api/v1/networks/{network_id}`
- `GET/POST /api/v1/networks/{network_id}/channels`
- `GET/PATCH /api/v1/networks/{network_id}/channels/{channel_id}`
- `GET /api/v1/agents` — built-in specialist agent catalogue
- `GET/POST /api/v1/networks/{network_id}/tasks` — task queue intake and inspection
- `GET /api/v1/networks/{network_id}/approvals` — pending and historical approvals
- `POST /api/v1/approvals/{approval_id}/decision` — approve or reject a gated external action

External-action tasks enter `awaiting_approval`; they cannot be dispatched until explicitly approved. This milestone supplies the persistent orchestration control plane, not yet an LLM execution runtime.
