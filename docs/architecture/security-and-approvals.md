# Security, Permissions, and Approval Controls

## Default-deny policy

All agent tools and external actions are denied unless explicitly granted. Every permission is scoped to a network, channel, action type, and where appropriate a specific resource.

## Roles

- Owner: full configuration and approval authority.
- Operator: manage channels and workflows within assigned permissions.
- Reviewer: review content and approve only assigned action classes.
- Read-only: inspect dashboards and reports.

Use server-side RBAC plus channel-level access checks. Do not rely on hidden frontend controls for authorization.

## Secrets and OAuth

- Never commit client secrets, access tokens, refresh tokens, cookies, or provider API keys.
- Store secrets in a secret manager or authenticated encrypted credential store; database rows hold references and non-secret metadata only.
- The AIMN API has versioned Fernet encryption helpers. Configure `AIMN_CREDENTIAL_ENCRYPTION_KEY` in a deployment secret store, separate from database backups. Rotation and persisted credential records remain to be implemented.
- Encrypt tokens at rest and in transit; restrict decryption to the integration service.
- Request only necessary OAuth scopes and show them to the owner.
- Support disconnect, token revocation, and credential rotation.
- Never log authorization headers, token values, or full secret-bearing request bodies.

## Approval classes

### Automatic, no external side effect
Research, drafts, internal analysis, rendering local files, quality checks, analytics interpretation.

### Configured low-risk actions
Internal task scheduling, moving content between internal workflow states, and generating private reports, within configured limits.

### Explicit user authorization required
Connecting accounts, uploading or scheduling videos, setting visibility, replying to comments, moderating comments, deleting/editing published resources, purchasing services, increasing budgets, creating accounts, and changing security settings.

A blanket statement that the network is autonomous is not a substitute for the required explicit consent for a particular YouTube API write action. The UI must show the target channel, exact action, content/resource, visibility, and consequences before execution. Store the consent/approval decision with the action record. If a workflow has a policy that permits a class of repeated actions, that policy itself must be deliberately configured by the owner, clearly scoped, revocable, and reviewed against current YouTube API policies before enabling it.

## Kill switch

Provide a network-wide pause and channel-level pause. Pausing prevents new work from being claimed and cancels safe-to-cancel internal jobs. It does not pretend to roll back already completed external actions. Emergency stop must be available from every dashboard page.

## Budgets

- Default paid-provider budget: zero.
- Per-network, per-channel, per-provider daily and monthly caps.
- Hard stop when a cap is reached; no automatic top-up or subscription purchase.
- Record estimates before a paid operation and actual cost after it.
- Alert the owner before approaching configured limits.

## Content governance

Before a video can enter an external publishing workflow, require:
- source/provenance manifest;
- factual and rights review;
- originality and repetitive-content checks;
- synthetic-media disclosure assessment where applicable;
- audience and made-for-kids assessment;
- title, description, thumbnail, and visibility validation;
- explicit approval/consent record for the proposed YouTube action.

High-risk claims and sensitive topics must be escalated to a human reviewer. Do not generate deceptive engagement, fake views, likes, subscriptions, or spam comments.

## Audit events

Record actor (human or agent), action, target, channel/network, policy decision, approval reference, timestamp, request correlation ID, outcome, and relevant non-secret metadata. Audit records are append-only for application roles.

## Relevant official policy

https://developers.google.com/youtube/terms/developer-policies
