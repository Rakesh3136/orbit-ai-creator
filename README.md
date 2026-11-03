# AI Media Network (AIMN) — YouTube Creator Platform

AIMN is the multi-agent control plane and command center for building and operating an original YouTube media business. The repository also contains the earlier ORBIT local media-production toolkit; it is a separate production subsystem and is not yet fully orchestrated by AIMN.

## Current engineering status

Implemented:
- FastAPI control plane, SQLAlchemy models and Alembic migrations.
- Single-owner sign-in with signed HttpOnly sessions.
- Next.js dashboard for networks, channel profiles, agents, tasks and approvals.
- Local deterministic specialist worker.
- Bounded CEO workflow: research → strategy → writing → fact-checking → production.
- Parent/child task tracking and result aggregation.
- Docker Compose stack for PostgreSQL, API, worker and dashboard.
- Existing ORBIT local episode production toolkit (script planning, narration, captions, FFmpeg rendering and provenance).
- Existing standalone YouTube OAuth/upload/analytics adapters in ORBIT. They are not yet connected to AIMN's dashboard, encrypted credential store or approval service.

Not yet production-complete:
- Live AI provider integration and real CEO reasoning.
- Live research and source verification.
- AIMN-to-ORBIT production handoff.
- Secure server-side OAuth connection and encrypted refresh-token storage.
- YouTube channel identity sync and Analytics integration in AIMN.
- End-to-end publishing from the AIMN approval workflow.
- Comment moderation/replies, retry/lease recovery, audit stream, cost controls and production deployment hardening.

## Architecture

```text
Owner Dashboard
    │
    ▼
AIMN API ── Networks / Channels / Tasks / Approvals
    │
    ▼
AI CEO (bounded deterministic workflow today)
    ├── Research specialist
    ├── Strategy specialist
    ├── Writer specialist
    ├── Fact-check specialist
    └── Producer specialist
    │
    ▼
ORBIT Production Toolkit (standalone today)
    ├── Script and render planning
    ├── Local narration and captions
    ├── FFmpeg rendering
    └── Asset provenance
    │
    ▼
YouTube adapter (standalone today; approval-gated private uploads)
```

## Run the AIMN stack with Docker

Requirements: Docker Engine and the Docker Compose plugin.

1. Copy `.env.example` to `.env`.
2. Set a strong database password, owner email and random session secret.
3. Generate `AIMN_OWNER_PASSWORD_HASH` using the secure instructions in [apps/api/README.md](apps/api/README.md).
4. Start the stack:

```bash
docker compose up --build -d
docker compose ps
```

Open the dashboard at http://localhost:3000. The API health endpoint is http://localhost:8000/health/ready. The API container applies Alembic migrations before starting; the worker starts after the API is healthy.

To inspect logs:

```bash
docker compose logs -f api worker web
```

To stop the stack:

```bash
docker compose down
```

To remove local database data too, use `docker compose down -v` (this permanently deletes the local database volume).

The Compose configuration sets the session cookie to non-secure for local HTTP only. A real HTTPS deployment must use secure cookies, a trusted origin, managed secrets, backups and an appropriate reverse proxy. Do not expose the development stack directly to the public internet.

## AIMN worker behavior

Create a network and an internal task with agent ID `ceo` from the dashboard or API. The worker creates five specialist planning tasks and aggregates their outputs. Current handlers are deterministic templates; no LLM or live research is connected. External-action tasks are never dispatched by the worker.

## ORBIT production toolkit

Install from the repository root:

```bash
python -m pip install -e ".[dev]"
orbit-doctor
orbit --demo-video --narration auto --output data/demo
```

For YouTube CLI dependencies, install `.[youtube]`. The OAuth helper and uploader currently operate independently of AIMN. Keep client secrets and token files out of Git.

## Safety

- External-action tasks are not dispatched by the AIMN worker.
- YouTube uploader in the ORBIT subsystem is private-only and requires explicit human approval.
- Never paste OAuth client JSON, refresh tokens, API keys or passwords into chat or source code.
- Do not assume YouTube monetization or revenue; eligibility and performance are determined by YouTube and the audience.

## Verification

GitHub Actions runs backend tests, frontend production build, and a deterministic ORBIT render smoke test. See [the AIMN roadmap](docs/roadmap.md) for remaining release gates.
