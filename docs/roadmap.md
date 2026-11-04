# AIMN Roadmap

## Milestone 1 — Repository and UI foundation
- [x] Architecture and agent contracts documented.
- [x] Responsive Next.js command-center shell.
- [x] FastAPI application skeleton.
- [x] PostgreSQL/Redis local infrastructure definition.
- [x] Initial GitHub Actions workflow.

## Milestone 2 — Network and channel data foundation
- [x] SQLAlchemy network and channel models.
- [x] Alembic migrations.
- [x] Network and channel management API.
- [x] Tests for API-key protection, channel creation, validation, updates and network scoping.
- [x] CI and production smoke workflows passing on the current foundation commit.

## Milestone 3 — Owner identity and secure integrations
- [x] Owner sign-in and signed HttpOnly session management (single owner; no RBAC yet).
- [x] Dashboard owner sign-in UI and cookie-based API client.
- [x] Dashboard reads networks, channels, agent catalogue, tasks and pending approvals.
- [x] Dashboard can create networks, channel profiles and internal agent tasks.
- [ ] RBAC and per-network/channel authorization.
- [ ] Server-side session revocation and CSRF hardening.
- [ ] Secret manager adapter and persisted encrypted OAuth credential records.\n- [x] Versioned authenticated-encryption helper for credential payloads (persistence and OAuth lifecycle remain open).
- [ ] Google OAuth connect/disconnect and scope display.
- [ ] YouTube channel identity verification.

## Milestone 4 — Agent and task runtime
- [x] Initial agent catalogue and task/approval API records.
- [x] Local deterministic worker for specialist planning tasks.
- [x] Bounded AI CEO workflow with five specialist child tasks and result aggregation (deterministic mode).
- [ ] Versioned agent registry, skills and tool permissions.
- [ ] Worker leases, stale-task recovery, retries and heartbeat.
- [ ] LLM provider adapters and budget/rate limits.
- [ ] Agent activity stream, audit trail and cost accounting.

## Milestone 5 — Research and content intelligence
- [ ] Live research provider adapters with citations and source validation.
- [ ] Evidence-backed niche scoring.
- [ ] Competitor and audience research.
- [ ] Content calendar and experiment tracking.

## Milestone 6 — Production and YouTube operations
- [ ] Script generation and quality workflows.
- [ ] Media asset and render job management.
- [ ] Existing production pipeline adapters and provenance.
- [ ] OAuth connection and YouTube Data API integration.
- [ ] Upload preparation, metadata validation and explicit action approval.
- [ ] Comment moderation/reply workflow with owner review.

## Milestone 7 — Learning and network scaling
- [ ] Analytics sync and channel dashboards.
- [ ] Strategy experiments and evaluation.
- [ ] Budget ledger and hard limits.
- [ ] Multi-channel portfolio reporting.
- [ ] Controlled agent and channel expansion.

## Release gate
AIMN is not production-complete until migrations, backend and frontend tests, OAuth integration tests, secret handling, recovery behavior, approval enforcement and a real end-to-end YouTube test channel have all passed. Never claim monetization or revenue is guaranteed.
