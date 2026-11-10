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

Configure `DATABASE_URL`, owner credentials, a long random `AIMN_SESSION_SECRET`, and `AIMN_CREDENTIAL_ENCRYPTION_KEY` in your local environment or deployment secret store. Generate the encryption key with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Keep the encryption key separate from the database and ciphertext backups. Never commit secrets or put the machine API key in browser code.

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

The worker runs deterministic local handlers. The Producer can pass a supplied script to the ORBIT renderer for local FFmpeg output; all other specialists remain planning-only. It does not call an LLM, perform live web research, access YouTube, read comments, or publish. Install both the root ORBIT package and the API package for this monorepo integration.

## AI CEO orchestration (current local mode)

Create an internal task with `agent_id: "ceo"`. The CEO creates at most five child tasks in this fixed workflow: research, strategist, writer, fact-checker and producer. Child tasks carry `parent_task_id`; once all are terminal, the CEO task aggregates their results. This is bounded deterministic orchestration, not yet an LLM-powered executive agent.

## Credential vault status

The API now includes authenticated encryption helpers for JSON credential payloads. The ciphertext envelope is versioned and authenticated; a missing or incorrect key fails closed. Configure `AIMN_CREDENTIAL_ENCRYPTION_KEY` outside source control. This is the cryptographic foundation only: database persistence, Google OAuth callback handling, token refresh, disconnect/revocation and channel linking are not yet enabled.

Publishing, comment replies and other external actions remain disabled in the worker, regardless of approval state. Real integrations require separate provider adapters, credential handling, action-specific approval checks and integration tests.


## Feedback and approved lessons

Owners can rate completed internal task outputs through `POST /api/v1/networks/{network_id}/tasks/{task_id}/evaluation`, list evaluations with `GET /api/v1/networks/{network_id}/evaluations`, and approve/reject proposed lessons with `POST /api/v1/evaluations/{evaluation_id}/lesson-decision`. Evaluations preserve task, network/channel, reviewer, agent, skill and registry provenance. Pending/rejected lessons are excluded from future local task context. Network lessons are shared within their network; channel lessons remain channel-specific. This is text retrieval, not model fine-tuning.
