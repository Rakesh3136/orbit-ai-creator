# AIMN Roadmap

## Milestone 1 — Repository and UI foundation
- [x] Architecture and agent contracts documented.
- [x] Responsive Next.js command-center shell.
- [x] FastAPI application skeleton.
- [x] PostgreSQL/Redis local infrastructure definition.
- [x] Initial GitHub Actions workflow.

## Milestone 2 — Network and channel data foundation
- [x] SQLAlchemy network and channel models.
- [x] Alembic initial migration.
- [x] Network and channel management API.
- [x] Temporary fail-closed API-key bootstrap guard.
- [x] Tests for API-key protection, channel creation, validation, updates and network scoping.
- [ ] Verify CI and migration against PostgreSQL.
- [ ] Connect the web dashboard to the API.

## Milestone 3 — Owner identity and secure integrations
- [ ] Owner sign-in and session management.
- [ ] RBAC and per-network/channel authorization.
- [ ] Secret manager adapter and encrypted OAuth credential storage.
- [ ] Google OAuth connect/disconnect and scope display.
- [ ] YouTube channel identity verification.

## Milestone 4 — Agent and task runtime
- [ ] Agent registry, versions, skills and tool permissions.
- [ ] Durable task and workflow records.
- [ ] Worker process and queue.
- [ ] CEO orchestration and typed agent handoffs.
- [ ] Agent activity stream and cost accounting.

## Milestone 5 — Research and content intelligence
- [ ] Research provider adapters.
- [ ] Evidence-backed niche scoring.
- [ ] Competitor and audience research.
- [ ] Content calendar and experiment tracking.

## Milestone 6 — Production and YouTube operations
- [ ] Script and quality workflows.
- [ ] Media asset and render job management.
- [ ] Existing ORBIT pipeline adapters and provenance.
- [ ] Upload preparation and explicit action approval.
- [ ] Comment moderation/reply workflow with consent controls.

## Milestone 7 — Learning and network scaling
- [ ] Analytics sync and channel dashboards.
- [ ] Strategy experiments and evaluation.
- [ ] Budget ledger and hard limits.
- [ ] Multi-channel portfolio reporting.
- [ ] Controlled agent and channel expansion.
