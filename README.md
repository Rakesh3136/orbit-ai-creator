# AI Media Network (AIMN) — YouTube Creator Platform

AIMN is the multi-agent control plane and command center for building and operating an original YouTube media business. The repository also contains the earlier ORBIT local media-production toolkit; it is a separate production subsystem and is not yet fully orchestrated by AIMN.

## Current engineering status

Implemented:
- FastAPI control plane, SQLAlchemy models and Alembic migrations.
- Single-owner sign-in with signed HttpOnly sessions and API-level cookie authentication.
- Next.js dashboard for networks, channel profiles, agents, tasks and approvals.
- Versioned agent/skill registry; each planning result records the registry and skill versions used.
- Zero-paid-provider baseline: no agent tools are enabled, paid-provider budget is USD 0, and external writes are denied.
- Local deterministic specialist worker.
- Owner-rated completed-task evaluations with skill and registry provenance.
- Network/channel-scoped reusable lessons; proposed lessons require explicit owner approval before future-task retrieval.
- Bounded CEO workflow: research → strategy → writing → fact-checking → production.
- Parent/child task tracking and result aggregation.
- Docker Compose stack for PostgreSQL, API, worker and dashboard.
- Existing ORBIT local episode production toolkit (script planning, narration, captions, FFmpeg rendering and provenance).
- Existing standalone YouTube OAuth/upload/analytics adapters in ORBIT. They are not yet connected to AIMN's dashboard, encrypted credential store or approval service.

Not yet production-complete:
- Live AI provider integration and real CEO reasoning.
- Live research and source verification.
- Model fine-tuning or autonomous self-training. The implemented feedback loop retrieves owner-approved text lessons; it does not train model weights.
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

Create a network and an internal task with agent ID `ceo` from the dashboard or API. The worker creates five specialist planning tasks and aggregates their outputs. Current handlers are deterministic templates; no LLM or live research is connected. Each result records the registry and skill versions used, plus the currently denied tools/write permissions and zero paid-provider allowance. This is a reproducible skill-configuration foundation, not model training. External-action tasks are never dispatched by the worker.

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


## Agent feedback and lesson memory

See [the feedback and memory guide](docs/agent-feedback-memory.md). Owners can rate completed internal task outputs, record corrections, and propose reusable lessons. Proposed lessons are pending until explicitly approved. Approved lessons are retrieved with network/channel scoping and skill-version provenance. This is local retrieval, not model fine-tuning.


## Install AIMN on Android

AIMN is being delivered as an installable Progressive Web App (PWA), so it opens in its own app window with an AIMN icon and does not require Play Store publication. The site must be reachable over HTTPS for full PWA installation.

1. Open the deployed AIMN HTTPS address in Chrome on Android.
2. Sign in to your owner account.
3. Tap Install app in the AIMN top bar when Chrome offers it, or open Chrome's three-dot menu and choose Install app / Add to Home screen.
4. Confirm. AIMN will appear as an app icon and open separately from the browser tab.

For local Docker testing on a computer, open http://localhost:3000 on that computer. To test from a phone on the same Wi-Fi, use the computer's LAN IP (for example, http://192.168.x.x:3000); that HTTP address is for testing and is not sufficient for full PWA installation. Do not expose the development Compose stack directly to the public internet.

The web container now proxies /api/* requests to the private API container. The browser no longer calls localhost:8000, which would incorrectly mean the Android phone itself when AIMN is opened on a phone. For a public HTTPS deployment, set AIMN_SESSION_COOKIE_SECURE=true and set the correct AIMN_WEB_ORIGIN in the deployment environment.
