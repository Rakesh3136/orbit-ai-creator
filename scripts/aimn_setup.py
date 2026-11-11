#!/usr/bin/env python3
"""Create a local AIMN .env without printing secrets or overwriting an existing file."""
from __future__ import annotations

import base64
import getpass
import hashlib
import re
import secrets
from pathlib import Path

ROUNDS = 310_000


def password_hash(password: str) -> str:
    salt = secrets.token_urlsafe(18)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), ROUNDS)
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return "pbkdf2_sha256$" + str(ROUNDS) + "$" + salt + "$" + encoded


def main() -> int:
    target = Path(".env")
    if target.exists():
        print("A .env file already exists. Nothing was changed.")
        return 1

    email = input("AIMN owner email: ").strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        print("Please enter a valid email address.")
        return 1

    while True:
        password = getpass.getpass("Create a strong AIMN owner password (16+ characters): ")
        if len(password) < 16:
            print("Use at least 16 characters.")
            continue
        if password != getpass.getpass("Confirm password: "):
            print("Passwords did not match. Try again.")
            continue
        break

    values = [
        "POSTGRES_PASSWORD=" + secrets.token_urlsafe(36),
        "AIMN_OWNER_EMAIL=" + email,
        "AIMN_OWNER_PASSWORD_HASH=" + password_hash(password),
        "AIMN_SESSION_SECRET=" + secrets.token_urlsafe(48),
        "AIMN_SESSION_TTL_SECONDS=43200",
        "AIMN_SESSION_COOKIE_SECURE=false",
        "AIMN_WEB_ORIGIN=http://localhost:3000",
        "AIMN_LLM_PROVIDER=none",
        "AIMN_OLLAMA_URL=http://ollama:11434",
        "AIMN_OLLAMA_MODEL=qwen2.5:3b",
        "",
    ]
    target.write_text("\n".join(values), encoding="utf-8")
    try:
        target.chmod(0o600)
    except OSError:
        pass
    print("Created .env. Keep it private; it contains server secrets and your owner password hash.")
    print("Next: docker compose up --build -d")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
