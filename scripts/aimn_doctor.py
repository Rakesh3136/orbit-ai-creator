#!/usr/bin/env python3
"""Preflight checks for a local AIMN Docker installation."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    print("AIMN setup check")
    failures = 0
    if shutil.which("docker") is None:
        print("MISSING  Docker CLI — install Docker Desktop or Docker Engine + Compose.")
        failures += 1
    else:
        print("OK       Docker CLI found")
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if result.returncode:
            print("MISSING  Docker Compose plugin — install the Docker Compose v2 plugin.")
            failures += 1
        else:
            print("OK       " + result.stdout.strip())
        daemon = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if daemon.returncode:
            print("NOT READY Docker daemon is not reachable. Start Docker Desktop / Docker Engine.")
            failures += 1
        else:
            print("OK       Docker daemon is reachable")
    env_file = root / ".env"
    if not env_file.is_file():
        print("MISSING  .env — run: python scripts/aimn_setup.py")
        failures += 1
    else:
        required = {"POSTGRES_PASSWORD", "AIMN_OWNER_EMAIL", "AIMN_OWNER_PASSWORD_HASH", "AIMN_SESSION_SECRET"}
        values = {}
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
        missing = sorted(key for key in required if not values.get(key))
        if missing:
            print("INVALID  .env is missing required values: " + ", ".join(missing))
            failures += 1
        else:
            print("OK       .env contains required settings (values hidden)")
    if failures == 0 and shutil.which("docker"):
        result = subprocess.run(["docker", "compose", "config", "--quiet"], cwd=root,
                                capture_output=True, text=True)
        if result.returncode:
            print("INVALID  Docker Compose configuration: " + (result.stderr.strip() or "validation failed"))
            failures += 1
        else:
            print("OK       Docker Compose configuration is valid")
    if failures:
        print(f"\n{failures} check(s) need attention. Fix them, then rerun this command.")
        return 1
    print("\nReady to start AIMN with: docker compose up --build -d")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
