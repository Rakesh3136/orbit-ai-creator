# AIMN Implementation Roadmap

This roadmap evolves the existing ORBIT creator engine into a multi-channel AI Media Network. Each phase has an acceptance gate; do not start broad feature work while the previous gate is failing.

## Phase 0 — Repository and baseline audit

- [x] Identify the current default branch and repository structure.
- [x] Confirm the existing creator pipeline, tests, YouTube adapter, and approval gate.
- [x] Record the target architecture and migration approach.
- [ ] Run the current test suite in a reproducible environment and capture baseline results.
- [ ] Review all branches and workflow history before any destructive cleanup.
- [ ] Confirm the current OAuth credential is not committed; rotate it if it was ever exposed.

Exit: reproducible baseline and a documented inventory of reusable modules and known defects.

## Phase 1 — Platform foundation

- [ ] Monorepo structure: `apps/web`, `apps/api`, `apps/worker`, `packages/contracts`, and `infra/`.
- [ ] FastAPI health/readiness endpoints and versioned API prefix.
- [ ] Next.js responsive shell with AI chat and command-center navigation.
- [ ] PostgreSQL migrations and tenant-scoped core models.
- [ ] Authentication, session security, owner role, and channel-level authorization.
- [ ] Redis-backed job queue with durable task state in PostgreSQL.
- [ ] Structured logging, request IDs, error reporting, and audit-event foundation.
- [ ] Local development compose file and documented setup.

Acceptance: owner can sign in, see an empty network dashboard, create a channel workspace record, and view health status. No external YouTube write action is enabled.

## Phase 2 — AI CEO and agent runtime

- [ ] CEO conversation API and persisted conversations.
- [ ] Agent registry with versioned definitions, skills, tools, and permission profiles.
- [ ] LangGraph workflow orchestration with checkpointing.
- [ ] Typed agent task/result events and live status updates to the web app.
- [ ] Human approval pause/resume flow.
- [ ] Model-provider adapter and local-model option.
- [ ] Agent trace, cost, latency, and failure dashboard.

Acceptance: user asks the CEO to research a topic; the CEO delegates to a research agent, displays progress, stores a source-backed report, and summarizes results.

## Phase 3 — Channel intelligence

- [ ] Global topic discovery and source verification.
- [ ] Channel-specific niche, audience, brand, and language profiles.
- [ ] Competitor and format research using permitted data sources.
- [ ] Opportunity scoring with uncertainty and evidence.
- [ ] Channel launch kit (name candidates, positioning, branding brief, content plan).
- [ ] Owner-controlled channel connection workflow.

Acceptance: produce an evidence-backed channel strategy and launch kit. Channel/account creation remains a human Google-account action.

## Phase 4 — Content factory

- [ ] Adapt ORBIT research and script modules to the new contracts.
- [ ] Script outlines, drafts, fact checking, localization, and quality review.
- [ ] Storyboard and shot-list generation.
- [ ] Image, audio, video, and 3D provider adapters.
- [ ] FFmpeg editing/render pipeline with resumable jobs.
- [ ] Captions, thumbnail assets, metadata, and provenance manifest.
- [ ] Rights, originality, and synthetic-media review.

Acceptance: generate a complete reviewable content package and playable draft from one approved idea.

## Phase 5 — YouTube operations

- [ ] Multi-account OAuth credential vault and channel identity mapping.
- [ ] Read-only channel/video/analytics synchronization.
- [ ] Upload and scheduling action preview.
- [ ] Explicit per-action consent/approval and immutable audit record.
- [ ] Comment triage and suggested replies; write operations gated by consent.
- [ ] Quota tracking, resumable uploads, retry safety, and error recovery.

Acceptance: complete a private test upload only after the owner approves the exact channel, video, and action. Public/scheduled publishing remains disabled until a separate policy review and explicit owner configuration.

## Phase 6 — Learning and network operations

- [ ] Cross-channel analytics with channel-isolated detail.
- [ ] Strategy experiments and outcome tracking.
- [ ] Cost/revenue ledger and budget guardrails.
- [ ] Weekly intelligence report and opportunity portfolio.
- [ ] New-channel proposal workflow and capacity checks.
- [ ] Network-level pause, per-channel pause, and incident alerts.

Acceptance: the CEO can compare channels, explain evidence, propose next experiments, and never exceed configured permissions or budgets.

## Engineering gates for every phase

- Unit tests for domain logic and permission boundaries.
- Integration tests for API/database/worker behavior.
- Contract tests for agent inputs and outputs.
- End-to-end tests for the primary user journey.
- Security checks for secret handling and tenant isolation.
- CI must pass before merge.
- No credentials or generated media artifacts in Git.
