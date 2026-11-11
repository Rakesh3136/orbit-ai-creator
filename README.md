# AI Media Network (AIMN)

AIMN is a local-first command center for managing a YouTube media operation with specialist agents. The repository includes the AIMN dashboard/API and the ORBIT local video-production toolkit.

## Quick start (Windows, macOS, Linux)

**Requirements:** a computer with Docker Desktop (Windows/macOS) or Docker Engine + Docker Compose v2 (Linux), and Python 3.11 or newer. AIMN is not hosted by GitHub; the computer running Docker hosts the local app.

1. Download or clone this repository and open a terminal in its root folder.
2. Run:

```bash
python scripts/aimn_start.py
```

On first run it asks you to create the owner email and password, writes private secrets to `.env`, checks Docker, builds the containers, and starts the app. Keep that terminal/computer and Docker running.

3. Open **http://localhost:3000** on the same computer and sign in with the owner credentials you created.

Useful commands:

```bash
python scripts/aimn_doctor.py                 # check Docker and private configuration
docker compose ps                             # see running services
docker compose logs -f api worker web         # view app logs
docker compose down                           # stop AIMN without deleting its database
python scripts/aimn_backup.py backup          # back up the database
python scripts/aimn_assets.py backup          # back up local media and memory assets
```

To start again later, use `docker compose up -d`. To rebuild after code updates, use `docker compose up --build -d`. Do not use `docker compose down -v` unless you intentionally want to delete the database volume.

## Use AIMN on Android

The dashboard is a Progressive Web App (PWA), not a Play Store app. The local launcher binds the web UI to the computer's network interfaces so a phone on the same trusted Wi-Fi can open the computer's LAN IP (for example `http://192.168.1.20:3000`). Allow port 3000 only on your private network in the computer firewall; never port-forward it to the public internet. Local HTTP is for testing only. For installable app behavior and secure owner sessions from outside the computer, deploy behind HTTPS, set `AIMN_SESSION_COOKIE_SECURE=true`, and set `AIMN_WEB_ORIGIN` to the exact public HTTPS origin. Then open the site in Chrome on Android → ⋮ → Install app / Add to Home screen.

AIMN is not publicly hosted by this repository. Public deployment requires a server or computer that remains online, HTTPS/reverse-proxy configuration, secure backups, and production hardening. Do not expose the development stack or PostgreSQL/API ports directly to the internet.

## What works today

- Owner login with signed HttpOnly sessions.
- Networks, channel profiles, agent catalogue, internal task queue and owner approvals.
- Bounded CEO workflow: research brief → channel strategy → Writer draft → fact-check plan → Producer.
- Deterministic local templates when no model is configured.
- Optional Ollama inference for Writer drafts, with no paid API. See [local AI setup](docs/local-ai.md).
- Owner feedback and approval-gated reusable text lessons. This is retrieval memory, not model-weight training.
- Local ORBIT rendering of a draft script to MP4, captions and provenance.
- Database and media/memory backup utilities.
- PWA metadata and install guidance.

## Important limitations

AIMN is a working foundation, not yet a fully autonomous monetized YouTube business. Live web research, source-backed automated fact checking, OAuth connection and encrypted YouTube token storage in AIMN, analytics sync, comment management, and approval-gated publishing are not complete. The standalone ORBIT YouTube helpers are not yet wired into the AIMN dashboard. YouTube publishing is not enabled by the worker. No revenue or monetization result is guaranteed.

## Zero-budget design

- No paid AI API is required.
- Local Ollama is optional; without it AIMN uses deterministic local templates.
- Docker and model downloads use your computer's storage, RAM, CPU and electricity.
- Free GitHub Actions are used for CI where available; GitHub is source control, not the runtime host.

## Security

Keep `.env`, OAuth client JSON, access tokens and refresh tokens private. Never commit them or paste them into chat. Local HTTP uses a non-secure cookie for localhost development; use HTTPS and `AIMN_SESSION_COOKIE_SECURE=true` for public deployment. Publishing and other external actions require separate owner approval and are not automatically executed.

## Documentation

- [Optional local AI model](docs/local-ai.md)
- [Portability and migration](docs/portability-and-migration.md)
- [Local database backup](docs/portability-and-migration.md)
- [Local asset backup](docs/local-asset-backup.md)
- [Agent feedback and memory](docs/agent-feedback-memory.md)
- [AIMN to ORBIT production handoff](docs/aimn-orbit-production-handoff.md)
