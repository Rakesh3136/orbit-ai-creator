# AIMN API

FastAPI control plane for the Autonomous AI Media Network.

## Local development

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn aimn_api.main:app --reload --app-dir src
```

Configure `DATABASE_URL` and a long random `AIMN_ADMIN_API_KEY`. Management routes fail closed when the key is missing. This API-key guard is a temporary single-operator bootstrap control, not final owner identity or role-based access control.

## Current control-plane endpoints

- `GET /health/live`, `GET /health/ready`
- `GET /api/v1/system`
- `GET/POST /api/v1/networks`
- `GET /api/v1/networks/{network_id}`
- `GET/POST /api/v1/networks/{network_id}/channels`
- `GET/PATCH /api/v1/networks/{network_id}/channels/{channel_id}`
- `GET /api/v1/agents` — built-in specialist agent catalogue
- `GET/POST /api/v1/networks/{network_id}/tasks` — task queue intake and inspection
- `GET /api/v1/networks/{network_id}/approvals` — pending and historical approvals
- `POST /api/v1/approvals/{approval_id}/decision` — approve or reject a gated external action

External-action tasks enter `awaiting_approval`; they cannot be dispatched until explicitly approved. This milestone supplies the persistent orchestration control plane, not yet an LLM execution runtime.

## Owner sign-in setup

Generate a PBKDF2-SHA256 hash locally. Your password is entered only into your terminal:

```bash
python - <<'PY'
import base64, getpass, hashlib, secrets
password = getpass.getpass('Owner password: ').encode()
salt = secrets.token_urlsafe(18)
digest = hashlib.pbkdf2_hmac('sha256', password, salt.encode(), 310000)
encoded = base64.urlsafe_b64encode(digest).decode().rstrip('=')
print(f'pbkdf2_sha256$310000${salt}${encoded}')
PY
```

Set the resulting value as `AIMN_OWNER_PASSWORD_HASH`, along with `AIMN_OWNER_EMAIL` and a randomly generated `AIMN_SESSION_SECRET` of at least 32 characters, in your deployment secret store. Do not commit real credentials. Use `AIMN_SESSION_COOKIE_SECURE=true` on HTTPS and `false` only for local HTTP. Authentication endpoints are `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, and `POST /api/v1/auth/logout`. The machine API key remains for trusted server-to-server calls only; do not put it in browser code.
