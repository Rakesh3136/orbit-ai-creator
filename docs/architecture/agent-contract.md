# Agent Execution Contract

## Purpose

Agents are specialized, observable workers coordinated by the AI CEO/orchestrator. An agent is not an unrestricted autonomous account.

## Required definition

Each agent definition must include:

```yaml
name: research.topic_discovery
version: 1
description: Discover and evaluate topic opportunities for one channel.
input_schema: ResearchRequest
output_schema: ResearchReport
tools:
  - approved_search_provider
  - youtube_data_api.readonly
memory_scope:
  read: [network_strategy, channel_strategy, prior_research]
  write: [research_reports]
side_effects: []
limits:
  timeout_seconds: 180
  max_retries: 2
  max_cost_usd: 0
permissions:
  channel_scope: assigned_channel_only
  external_writes: false
```

## Agent lifecycle

1. Orchestrator creates a task with a unique ID, channel scope, deadline, and idempotency key.
2. Worker claims the task using a lease.
3. Input is validated against the agent's declared schema and permission scope.
4. Agent executes only approved tools.
5. Output is validated and stored with provenance, citations, model/provider metadata, and usage.
6. Agent emits a typed result event.
7. Orchestrator evaluates the result and either schedules the next step, retries safely, marks the task failed, or requests human approval.
8. All state transitions are recorded.

## Communication

Use typed events such as:

- task.created
- task.started
- task.progress
- task.completed
- task.failed
- agent.message
- approval.requested
- approval.decided
- workflow.paused
- workflow.resumed

An agent message includes sender, recipient/department, network_id, optional channel_id, task_id, correlation_id, timestamp, message_type, and a schema-validated payload. Do not treat arbitrary agent-generated text as executable instructions.

## Failure and recovery

- Retry only transient failures and only within a bounded retry policy.
- Use exponential backoff with jitter for provider/network errors.
- Do not retry non-idempotent external writes automatically.
- Persist workflow checkpoints before and after expensive steps.
- A failed agent must return a structured error and recovery suggestion.
- The orchestrator may reassign work, but must preserve task history and avoid duplicate side effects.

## Memory

Memory is scoped and sourced:
- Network memory: owner preferences, global budgets, cross-channel learnings.
- Channel memory: audience, brand voice, content history, experiments.
- Task memory: short-lived context for one workflow.
- Evidence store: source documents, claims, timestamps, and provenance.

A memory item stores origin, scope, created_at, last_verified_at, confidence, and retention policy. Do not write guesses or unverified claims into durable strategic memory.

## Initial agent departments

1. Research & intelligence: topic discovery, competitor analysis, audience research, source verification.
2. Channel strategy: niche scoring, brand identity, editorial calendar.
3. Editorial: outline, script, hook, localization, fact-checking.
4. Creative production: shot plan, image/3D/video prompts, narration, captions.
5. Post-production: assembly, pacing, subtitles, audio mix, render validation.
6. Growth: title/thumbnail experiments, metadata, analytics interpretation.
7. Publishing & community: upload preparation, scheduled publishing, comment triage and approved replies.
8. Governance: quality, originality, rights/provenance, policy and risk checks.
9. Business intelligence: revenue/cost ledger, channel comparison, opportunity portfolio.

Start with a small set of working agents and add specializations when the workflow demonstrates a need. Do not instantiate dozens of agents merely to make the dashboard look populated.
