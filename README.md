# ORBIT — Autonomous Media Creator

ORBIT is a local-first, $0-start AI creator system for building an original YouTube media brand.

## What ORBIT does

```text
Discover → Research → Idea scoring → Script → Quality gate
    → Narration → Captions → Visual composition → MP4 render
    → Publishing package → Human approval → YouTube upload
    → Analytics → Learning → Next episode
```

The system is deliberately built as an original-media workflow rather than a mass-production bot.

## Current capabilities

- Zero-cost public RSS research bootstrap
- Idea ranking and quality scoring
- Deterministic script drafting
- Optional local Ollama script generation
- Fact/uncertainty tracking in the research model
- Local SQLite memory
- Render-plan generation
- Free/local narration through `espeak-ng` or `espeak`
- Silent-render fallback for machines without TTS
- SRT caption generation
- Full FFmpeg episode rendering
- Asset SHA-256 provenance registry
- Publishing-package generation
- YouTube OAuth 2.0 adapter
- YouTube private/unlisted/public upload adapter
- YouTube analytics adapter
- Analytics-to-strategy learning engine
- Environment diagnostics
- Automated unit/production CI

## $0-first local setup

Requirements:

- Python 3.11+
- FFmpeg
- Optional: espeak-ng for free local narration
- Optional: Ollama + a local model for richer script generation
- Optional: Google Cloud project + YouTube Data API OAuth credentials for channel upload

Install:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Check the machine:

```bash
orbit-doctor
```

Generate a deterministic end-to-end demo video without web research:

```bash
orbit --demo-video --narration auto --output data/demo
```

This produces:

```text
data/demo/
├── orbit_demo.mp4
├── orbit_demo.srt
├── asset_provenance.json
└── package/
    ├── script.txt
    ├── render_plan.json
    └── publishing_package.json
```

Run research and generate a publishing package:

```bash
orbit "artificial intelligence and the future of work" --package --output data/episode
```

Render a researched episode locally:

```bash
orbit "artificial intelligence and the future of work" --render-video --narration auto --output data/episode
```

## Optional local model

ORBIT can use a local Ollama server without a paid API:

```bash
set ORBIT_LLM_PROVIDER=ollama
set ORBIT_OLLAMA_MODEL=<your-local-model-name>
```

On PowerShell use `$env:ORBIT_LLM_PROVIDER` and `$env:ORBIT_OLLAMA_MODEL` instead.

If the local model is unavailable or returns malformed output, ORBIT falls back to its deterministic writer so CI remains reproducible.

## YouTube connection

Install the optional integration:

```bash
python -m pip install -e '.[youtube]'
```

Create a Google OAuth desktop client for the YouTube Data API and place the downloaded client secret file at:

```text
client_secret.json
```

Then run:

```bash
orbit-connect-youtube
```

The resulting `token.json` is ignored by Git. ORBIT requests only the YouTube upload scope and the application defaults to private uploads. Credentials do not imply publishing permission; the V1 publish gate still requires explicit human approval.

## CI

Two GitHub Actions workflows protect the project:

1. `test.yml` installs the package, verifies imports/bytecode, and runs the Python test suite.
2. `production-smoke.yml` installs FFmpeg + espeak-ng, renders a complete deterministic episode, validates the MP4/SRT/provenance files, and uploads them as an artifact.

## Monetization strategy

ORBIT is designed to build audience first and monetize legitimately through YouTube and other channel-relevant revenue streams once eligible. It does not attempt to bypass platform eligibility or automate misleading/repetitive content.

## Safety and originality

ORBIT blocks publication when quality is below threshold or human approval is absent. Sensitive topics, legal allegations, medical/financial claims, political persuasion, copyright uncertainty, sponsorship contracts, and account/security changes require additional human review.

Every asset should have documented provenance. The V1 renderer generates its own backgrounds and local narration so the demo does not depend on stock footage or copyrighted third-party media.

## Roadmap status

The engineering baseline is complete for a local-first V1/V2 creator loop. Remaining real-world setup is limited to external services that cannot be completed from source code alone: the user's Google OAuth authorization and any final channel/account configuration.
