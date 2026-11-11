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
- [x] Owner login, logout, cookie attributes, signature tampering and dashboard API access tests.
- [x] Dashboard owner sign-in UI and cookie-based API client.
- [x] Dashboard reads networks, channels, agent catalogue, tasks and pending approvals.
- [x] Dashboard can create networks, channel profiles and internal agent tasks.
- [ ] RBAC and per-network/channel authorization.
- [x] PWA manifest, app icon, service-worker registration and Android install entry point.
- [x] Same-origin API proxy so Android clients do not call their own localhost.
- [ ] HTTPS production hosting and Android device install verification.
- [ ] Server-side session revocation, login rate limiting and additional CSRF hardening.
- [ ] Secret manager adapter and persisted encrypted OAuth credential records.
- [x] Versioned authenticated-encryption helper for credential payloads (persistence and OAuth lifecycle remain open).
- [ ] Google OAuth connect/disconnect and scope display.
- [ ] YouTube channel identity verification.

## Milestone 4 — Agent and task runtime
- [x] Initial agent catalogue and task/approval API records.
- [x] Local deterministic worker for specialist planning tasks.
- [x] Bounded AI CEO workflow with five specialist child tasks and result aggregation (deterministic mode).
- [x] Versioned agent/skill registry; planning results record the skill version used.
- [x] Initial registry denies paid-provider spend, tool access and external writes by default.
- [ ] Worker leases, stale-task recovery, retries and heartbeat.
- [x] Owner-rated completed-task evaluations with correction and skill/registry provenance.
- [x] Pending/approved/rejected lessons with explicit owner decision and network/channel scope.
- [x] Approved lesson retrieval in future matching local task context (not model fine-tuning).
- [ ] Quality trend reporting, lesson expiry/versioning and memory conflict resolution.
- [ ] LLM provider adapters and budget/rate limits (only if a genuinely useful free/local model is selected).
- [ ] Agent activity stream, audit trail and cost accounting.

## Milestone 5 — Research and content intelligence
- [ ] Live research provider adapters with citations and source validation.
- [ ] Evidence-backed niche scoring.
- [ ] Competitor and audience research.
- [ ] Content calendar and experiment tracking.

## Milestone 6 — Production and YouTube operations
- [x] Deterministic local writer creates a structured draft script and hands it to the Producer; drafts remain explicitly unverified.\n- [ ] Evidence-backed script generation and quality workflows.
- [ ] Media asset and render job management.
- [x] Producer task can hand a supplied script to ORBIT for local FFmpeg rendering, captions, provenance and a private-by-default package.
- [x] Dashboard Producer form and authenticated task-scoped artifact downloads.
- [x] Existing production pipeline adapter and provenance for owner-supplied or writer-generated local drafts.
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
