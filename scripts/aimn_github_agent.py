#!/usr/bin/env python3
"""GitHub Actions-compatible, zero-dependency AIMN task runner.

This is a bounded planning runner, not an LLM and not an always-on service.
It writes an auditable JSON run record for the GitHub-only operating mode.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

PROFILES = {
    "restricted": {
        "description": "Read/planning only; no external writes.",
        "external_actions": False,
        "repository_writes": False,
        "requires_owner_approval": True,
    },
    "balanced": {
        "description": "Internal planning and repository run-record persistence.",
        "external_actions": False,
        "repository_writes": True,
        "requires_owner_approval": True,
    },
    "expanded": {
        "description": "Expanded internal workflow planning; external actions remain disabled.",
        "external_actions": False,
        "repository_writes": True,
        "requires_owner_approval": True,
    },
}

TASK_STEPS = {
    "research": [
        "Break the objective into verifiable research questions.",
        "Identify primary sources that a future research connector should consult.",
        "Separate known facts, assumptions, and unanswered questions.",
        "Prepare a research brief; do not claim that live research occurred.",
    ],
    "strategy": [
        "Define the intended audience and the viewer problem.",
        "Propose a channel position and repeatable content pillars.",
        "Define a small experiment and measurable success criteria.",
        "Require review of evidence before scaling.",
    ],
    "script": [
        "Create a script outline from the supplied objective.",
        "Mark factual claims as unverified until supported by sources.",
        "Prepare title, hook, body, and conclusion sections.",
        "Require editorial review before production or publication.",
    ],
    "production_check": [
        "Check that an approved script and rights-cleared assets are available.",
        "Prepare a scene, narration, captions, and export checklist.",
        "Keep the output private and unpublished.",
        "Require owner approval before any external upload.",
    ],
}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-type", choices=sorted(TASK_STEPS), required=True)
    parser.add_argument("--instruction", required=True)
    parser.add_argument("--access-profile", choices=sorted(PROFILES), default="restricted")
    parser.add_argument("--output-dir", default="aimn-state/runs")
    args = parser.parse_args()

    instruction = re.sub(r"\s+", " ", args.instruction).strip()
    if not instruction or len(instruction) > 2000:
        parser.error("instruction must contain 1–2000 non-whitespace characters")
    secret_pattern = re.compile(
        r"\b(?:github_pat_|gh[pousr]_|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20,}|ya29\.[0-9A-Za-z_-]{20,})"
        r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
        r"|\b(?:password|client_secret|access_token|refresh_token)\s*[:=]\s*\S+",
        re.IGNORECASE,
    )
    if secret_pattern.search(instruction):
        parser.error("instruction appears to contain a credential; remove it before running AIMN")

    now = datetime.now(timezone.utc)
    run_id = os.getenv("GITHUB_RUN_ID", f"local-{now.strftime('%Y%m%dT%H%M%SZ')}")
    profile = PROFILES[args.access_profile]
    record = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": now.isoformat(),
        "execution": "github_actions_ephemeral_runner",
        "mode": "bounded_planning_only",
        "task_type": args.task_type,
        "instruction": instruction,
        "access_profile": args.access_profile,
        "permissions": profile,
        "agent_output": {
            "status": "planned",
            "provider": "none",
            "model_inference": False,
            "live_web_research": False,
            "steps": TASK_STEPS[args.task_type],
            "summary": (
                "AIMN created a bounded execution plan. No external service was accessed, "
                "no model was trained or queried, and no content was published."
            ),
        },
        "safety": {
            "external_writes_performed": False,
            "publishing_enabled": False,
            "secrets_read": False,
            "owner_approval_required_for_sensitive_actions": True,
        },
        "limitations": [
            "GitHub Actions is a temporary job runner, not a continuously running backend.",
            "This initial runner creates plans; it does not perform live research or model inference.",
            "The access profile is an application policy and cannot expand GitHub token scopes.",
            "No permission profile grants literal unlimited access.",
        ],
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{run_id}.json"
    target.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved AIMN run record: {target}")
    print("Mode: bounded planning only; external actions disabled.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
