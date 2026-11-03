# AIMN — Autonomous AI Media Network

## Purpose

Evolve ORBIT from a single-channel, local-first creator pipeline into a web-operated, multi-channel media network. The product has two experiences backed by one platform:

1. Conversational AI CEO: the primary natural-language interface for the owner.
2. Operations command center: channels, agents, tasks, content, approvals, analytics, costs, and system health.

The network may research opportunities globally and propose new channels. Each channel has its own identity, audience, language, strategy, content calendar, connected YouTube account, and performance history. Shared services provide orchestration, research infrastructure, production capabilities, governance, and reporting.

## Product principles

- Build for multiple channels from day one; validate with one connected channel first.
- Preserve ORBIT's existing research, script, media-rendering, provenance, YouTube adapter, and learning code where it is reliable.
- Agents are bounded workers with explicit roles, tools, memory scopes, and permissions—not independent uncontrolled chatbots.
- All external actions are auditable and idempotent where possible.
- The system is provider-agnostic: model, search, TTS, image, and video providers are adapters.
- Start local-first and low-cost; paid services are optional and must have explicit budgets.
- No claim that YouTube's proprietary recommendation algorithm can be known or guaranteed.
- Generate original, useful content; do not optimize for mass-produced repetitive or misleading uploads.

## Logical architecture

```text
Browser (Next.js web app)
  ├── AI CEO chat
  ├── Network dashboard
  ├── Channel workspaces
  ├── Agent/task monitor
  ├── Content studio
  ├── Approval center
  └── Analytics and cost views
          │ HTTPS / WebSocket
          ▼
FastAPI application
  ├── Authentication and RBAC
  ├── Network and channel APIs
  ├── CEO conversation API
  ├── Agent/task APIs
  ├── Approval and audit APIs
  └── YouTube integration API
          │
          ├── PostgreSQL + pgvector (system of record)
          ├── Redis (queue/cache; never the only source of truth)
          ├── Object storage (media and artifacts)
          └── Worker processes
                ├── LangGraph orchestration
                ├── Research and strategy agents
                ├── Script and quality agents
                ├── Image/audio/video production adapters
                ├── Publishing and community adapters
                └── Analytics and learning workers
```

## Service boundaries

### Web application
Next.js + TypeScript. Responsive from mobile to desktop. The chat is a first-class route, while dashboard pages expose the same underlying jobs and state. The browser never receives provider secrets or refresh tokens.

### API and domain layer
Python + FastAPI. Owns validation, authorization, business rules, database transactions, API contracts, and audit events. The API does not execute long video renders in request handlers.

### Orchestration
LangGraph coordinates bounded workflows and agent handoffs. A workflow state is persisted and can pause for an approval. Agents return structured results and proposed actions; only authorized tool adapters can perform side effects.

### Workers
Background workers process research, script generation, rendering, thumbnail generation, analytics sync, and other long-running tasks. Jobs have retry limits, timeouts, deduplication keys, and observable states.

### Data
PostgreSQL is the authoritative store for users, networks, channels, agents, jobs, content, approvals, and audit events. pgvector is used only for retrieval features that justify embeddings. Redis is disposable infrastructure for queues/cache, not durable memory. Large media files live in object storage; the database stores metadata and checksums.

### Existing ORBIT package
Treat the current `orbit/` package as a domain capability library during migration. Wrap its research, scripting, rendering, provenance, YouTube, and learning modules behind service interfaces. Do not rewrite them wholesale before tests and behavior are understood.

## Core domain model

- User: authenticated human owner/operator.
- Network: one user's media business and global settings.
- Channel: an independent brand and YouTube channel configuration within a network.
- ChannelPolicy: locale, audience, niche, content rules, publishing rules, budget, and approval thresholds.
- AgentDefinition: versioned role, skills, tools, prompt/configuration, and permission profile.
- AgentRun: one execution with inputs, outputs, token/cost usage, status, and trace.
- Task: durable unit of work, owner, channel scope, priority, dependencies, retry state, and deadline.
- WorkflowRun: persisted multi-step graph execution, including pause/resume state.
- ContentIdea, ResearchBrief, Script, MediaAsset, VideoProject, PublishingPackage: content lifecycle records.
- ApprovalRequest: exact proposed external action, target channel/resource, visibility, rationale, expiry, and decision.
- ExternalAccount: encrypted OAuth credential reference and authorized scopes.
- AnalyticsSnapshot and StrategyExperiment: observations, time window, source, and bounded recommendations.
- BudgetLedger: per-network/channel/provider limits and recorded usage.
- AuditEvent: immutable record of sensitive reads, decisions, and side effects.

Every channel-owned record carries a `channel_id`; network-wide records carry a `network_id`. Authorization checks enforce tenant and channel boundaries.

## Agent contract

Every agent declares:
- stable name and version;
- one narrow responsibility;
- accepted input and output schemas;
- allowed tools and data scopes;
- timeout, retry, and cost limits;
- memory read/write scope;
- permitted side effects (default: none);
- evaluation criteria and failure behavior.

Agents communicate through typed task/result events. They do not directly mutate arbitrary database tables or call other agents through ad hoc prompt text. The orchestrator validates outputs and decides the next step.

## Initial deployment topology

Development: one repository, separate `apps/web`, `apps/api`, and `apps/worker` processes, PostgreSQL, Redis, and local object storage. Production can split workers and media services horizontally without changing domain contracts.

Avoid Kubernetes and microservice sprawl in the first milestone. Start as a modular monolith plus independent worker process; split services only when measured load or isolation needs justify it.

## YouTube integration boundary

Use documented YouTube Data API and YouTube Analytics API operations only. Each external account is explicitly connected by the owner through OAuth and displays its granted scopes. The product must clearly identify the channel and the exact YouTube action being proposed. Uploads, replies, moderation, visibility changes, and other write operations pass through a user-consent/approval policy and an auditable action adapter. Never scrape YouTube pages or use undocumented endpoints.

The YouTube Data API does not provide a general channel-creation operation for creating arbitrary new channels. Channel/account creation and ownership setup remain a human Google-account step; the platform can prepare a launch kit and connect channels the owner authorizes.

## Official references

- YouTube Data API overview: https://developers.google.com/youtube/v3/getting-started
- YouTube Data API reference: https://developers.google.com/youtube/data/reference/rest
- YouTube videos.insert: https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- YouTube API Services Developer Policies: https://developers.google.com/youtube/terms/developer-policies
- YouTube Data API revision history and quota changes: https://developers.google.com/youtube/data/revision_history
