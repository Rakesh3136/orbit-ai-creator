# ORBIT — Autonomous Media Creator

ORBIT is a local-first, $0-start AI creator system for building an original YouTube media brand.

## Mission

Discover strong stories, research them, write original scripts, fact-check claims, prepare production assets, publish to YouTube, measure performance, and improve the next episode.

## Current V0.2 capabilities

- Research and idea discovery
- Script drafting and quality scoring
- SQLite local memory
- Render-plan generation
- FFmpeg title-card rendering when FFmpeg is installed
- YouTube publishing-package generation
- Optional YouTube OAuth 2.0 integration
- Optional YouTube upload adapter using `videos.insert`
- Optional YouTube analytics adapter
- Automated tests in GitHub Actions

## $0-first architecture

- Python 3.11+
- SQLite for local memory
- FFmpeg for local video assembly
- Pluggable model/provider interfaces
- YouTube Data API with OAuth 2.0
- No credentials committed to Git

Install optional YouTube dependencies only when you are ready to connect the channel:

```bash
pip install -e '.[youtube]'
```

Basic local commands:

```bash
orbit --discover
orbit "artificial intelligence and the future of work" --package
orbit "artificial intelligence and the future of work" --render-title-card
```

The default flow remains local and human-reviewed.

## YouTube safety

ORBIT does not treat the presence of credentials as permission to publish. The publish gate requires a passing quality score and explicit human approval. The YouTube adapter uses the upload scope and defaults to private uploads at the application layer.

YouTube's current API documentation states that `videos.insert` is the upload method and that OAuth 2.0 is required for authorized insert/update/delete requests. Unverified API projects uploading videos are currently restricted to private viewing until the project completes the required audit. See the official documentation links in the project issues/release notes.

## Quality / originality

ORBIT must not mass-produce repetitive videos. Every episode needs a meaningful viewer promise, original editorial treatment, evidence-backed claims, and a quality gate before publishing.

Sensitive content, legal allegations, medical/financial claims, political persuasion, copyright uncertainty, sponsorship contracts, and account/security changes require human review.

## Roadmap

1. Finish V1 production pipeline
2. Add local/open model adapter for richer script and visual generation
3. Add asset licensing/provenance tracking
4. Connect YouTube channel through OAuth
5. Upload first private test video
6. Collect analytics
7. Improve the creator from observed performance
8. Enable carefully bounded autonomous publishing only after the system proves reliable
