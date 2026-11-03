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

## Local setup

### AIMN API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn aimn_api.main:app --reload --app-dir src
```

Set owner email, a PBKDF2 password hash, a random session signing secret (at least 32 characters), and database URL in local environment variables. Never commit credentials.

### AIMN worker

In a second terminal:

```bash
cd apps/api
python -m aimn_api.worker --poll-seconds 3
```

Create a network and an internal task using agent ID `ceo` from the dashboard or API. The worker creates five specialist planning tasks and aggregates their outputs. Current handlers are deterministic templates; no LLM or live research is connected.

### ORBIT production toolkit

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
