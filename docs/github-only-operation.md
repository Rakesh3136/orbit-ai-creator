# GitHub-only AIMN operation

## Target experience

AIMN is being adapted for an Android-first, GitHub-hosted control experience:

1. A static web/PWA console is published with GitHub Pages.
2. The owner connects one GitHub repository using a fine-grained token.
3. The owner selects an application permission profile.
4. The console dispatches a finite GitHub Actions job.
5. The runner creates a bounded plan and an auditable JSON record.
6. The owner reviews workflow status and controls the next action.

## Honest platform boundary

GitHub Pages serves static files; it does not run a persistent API server. GitHub Actions runs finite jobs and is not a 24/7 worker or database. The GitHub-only design therefore uses workflow dispatch and versioned repository state. It must not claim to provide always-on agents, unlimited compute, permanent background execution, or guaranteed model inference.

The existing Docker/FastAPI/PostgreSQL application remains a separate local/server runtime and is not the GitHub Pages runtime.

## Permission profiles

- `restricted`: planning only; the run record is available as a downloadable Actions artifact for 30 days and is not committed to the repository.
- `balanced`: planning plus an internal run-record commit under `aimn-state/runs/`.
- `expanded`: currently the same repository-write scope as balanced; reserved for future internal tools after review. It grants no additional GitHub scopes today.

The workflow enforces these profiles with separate job permissions. The planning job has `contents:read`. The separate persistence job receives `contents:write` only for balanced/expanded runs and is skipped for restricted runs.

The mobile console uses a fine-grained, single-repository token with Actions read/write and Contents read-only. The token is held in page memory only; it is not stored in browser storage and is never included in task prompts. Disconnect or close the page to clear it, and revoke it in GitHub settings when no longer needed. Never use a classic all-repositories PAT.

## Non-negotiable approval gates

Even in the expanded profile, require a fresh owner approval for:
- YouTube publishing, scheduling, or changing visibility;
- sending replies or messages;
- creating or changing accounts and OAuth grants;
- spending money or subscribing to services;
- changing repository permissions, workflows, secrets, or destructive files;
- deleting user data or replacing backups.

No mode means literal unlimited access. All external actions need a specific integration, the minimum required credential scope, an audit record, and an approval step.

## Current GitHub Actions runner

Run **Actions → AIMN agent run → Run workflow** on branch `feature/aimn-foundation`. Choose a task type, enter an instruction without secrets, and select an access profile. The runner rejects common credential patterns and creates a JSON plan record. It does not perform live web research, model inference, YouTube operations, or video publishing.

Restricted runs retain the record as a downloadable Actions artifact for 30 days. Balanced and expanded runs additionally commit the record to `aimn-state/runs/`. Do not put personal data, OAuth files, access tokens, or passwords in task instructions or run records.

## Publishing the owner console

The repository owner must enable **Settings → Pages → Build and deployment → Source: GitHub Actions**. The deployment workflow cannot enable Pages because the repository's Actions token does not have repository-administration permission. After Pages is enabled, the workflow deploys the contents of `apps/console/`. The expected URL is `https://rakesh3136.github.io/orbit-ai-creator/`.

## Completion checklist

- [ ] Owner enables GitHub Pages and the deployment succeeds.
- [x] Mobile-first console and initial connection/setup screen are implemented.
- [x] Owner can select restricted, balanced, or expanded application policy.
- [x] Fine-grained token is held in page memory only, with disconnect control.
- [x] Console can dispatch the bounded workflow and list recent run status.
- [x] Runner permission-profile tests and credential-input rejection tests pass in CI.
- [ ] Console can inspect and display generated plan records directly.
- [ ] Persistent agent memory, backup, retention, and privacy controls are implemented for GitHub-only operation.
- [ ] Live research and a free/open model inference path are integrated and evaluated.
- [ ] YouTube OAuth, analytics, comments, and upload integrations are implemented with explicit per-action approval.
- [ ] End-to-end owner approval and external-action audit workflows are tested.

The current GitHub-only console is an early operational foundation, not yet the completed autonomous creator system.
