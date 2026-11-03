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

Configure `DATABASE_URL`, owner credentials and a long random `AIMN_SESSION_SECRET` in your local environment or deployment secret store. Never commit secrets or put the machine API key in browser code.

## Current control-plane endpoints

- `GET /health/live`, `GET /health/ready`
- `GET /api/v1/system`
- `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`
- `GET/POST /api/v1/networks`
- `GET/POST/PATCH /api/v1/networks/{network_id}/channels`
- `GET /api/v1/agents`
- `GET/POST /api/v1/networks/{network_id}/tasks`
- `GET /api/v1/networks/{network_id}/approvals`
- `POST /api/v1/approvals/{approval_id}/decision`

External-action tasks enter `awaiting_approval`. The worker intentionally never dispatches them.

## Local planning worker

Apply database migrations first:

```bash
cd apps/api
alembic upgrade head
python -m aimn_api.worker --once
python -m aimn_api.worker --poll-seconds 3
```

The worker runs deterministic planning handlers. It does not call an LLM, perform live web research, access YouTube, generate media, read comments, or publish.

## AI CEO orchestration (current local mode)

Create an internal task with `agent_id: "ceo"`. The CEO creates at most five child tasks in this fixed workflow: research, strategist, writer, fact-checker and producer. Child tasks carry `parent_task_id`; once all are terminal, the CEO task aggregates their results. This is bounded deterministic orchestration, not yet an LLM-powered executive agent.

Publishing, comment replies and other external actions remain disabled in the worker, regardless of approval state. Real integrations require separate provider adapters, credential handling, action-specific approval checks and integration tests.
