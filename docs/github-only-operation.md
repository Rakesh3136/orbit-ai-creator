# GitHub-only AIMN operation

## Target experience

AIMN is being adapted for an Android-first, GitHub-hosted control experience:

1. A static web/PWA console is published with GitHub Pages.
2. The owner completes setup and selects an application permission profile.
3. The console starts a GitHub Actions workflow for each task.
4. An ephemeral Actions runner executes a bounded job.
5. The runner saves an auditable run record in `aimn-state/runs/`.
6. The owner reviews results and explicitly approves sensitive actions.

## Honest platform boundary

GitHub Pages serves static files; it does not run a persistent API server. GitHub Actions runs finite jobs and is not a 24/7 worker or database. The GitHub-only design therefore uses workflow dispatch and versioned repository state. It must not claim to provide always-on agents, unlimited compute, permanent background execution, or guaranteed model inference.

The existing Docker/FastAPI/PostgreSQL application remains a separate local/server runtime and is not the GitHub Pages runtime. It must not be presented as already deployed on GitHub Pages.

## Permission profiles

- `restricted`: planning/read-only application policy.
- `balanced`: internal planning plus repository run-record persistence.
- `expanded`: expanded internal planning workflow. External actions remain disabled until separately implemented and explicitly approved.

The workflow enforces these profiles with separate job permissions: the planning job has `contents:read`; the separate persistence job receives `contents:write` only for balanced/expanded runs. The browser token is only used to dispatch/read Actions; it does not get repository write access from the console. The mobile console uses a fine-grained, single-repository token held in page memory only; it is not stored in browser storage and is never included in task prompts. Disconnect or close the page to clear it, and revoke it in GitHub settings when no longer needed. Never use a classic all-repositories PAT.

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

Run **Actions → AIMN agent run → Run workflow** on branch `feature/aimn-foundation`. Choose a task type, enter an instruction without secrets, and select an access profile. The first runner creates a JSON plan record; it does not perform live web research, model inference, YouTube operations, or video publishing.

Run records are committed to `aimn-state/runs/` and become part of repository history. Do not put personal data, OAuth files, access tokens, or passwords in task instructions or run records.

## Completion criteria for the GitHub-only edition

- [ ] GitHub Pages console is deployed and mobile responsive.
- [ ] First-run setup wizard and owner-controlled permission profile are implemented.
- [ ] Browser authorization is narrowly scoped, session-only, and revocable.
- [ ] Console can dispatch workflows and display run status/results.
- [ ] Agent state and memory have documented backup, retention, and privacy controls.
- [ ] Workflow execution is bounded, auditable, and tested.
- [ ] All sensitive integrations have explicit per-action approvals.
- [ ] Documentation clearly distinguishes planning, model inference, verified research, and completed external actions.
