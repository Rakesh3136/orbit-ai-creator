#!/usr/bin/env python3
"""One-command local AIMN setup and startup."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def run(command: list[str], cwd: Path) -> int:
    return subprocess.run(command, cwd=cwd).returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if not (root / ".env").exists():
        print("First-time setup: create your private AIMN owner account.")
        if run([sys.executable, "scripts/aimn_setup.py"], root):
            return 1
    from aimn_doctor import main as doctor_main
    if doctor_main():
        return 1
    print("\nBuilding and starting AIMN. The first build can take several minutes...")
    if run(["docker", "compose", "up", "--build", "-d"], root):
        print("AIMN did not start. Inspect logs with: docker compose logs --tail=150 api worker web")
        return 1
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        try:
            with urlopen("http://127.0.0.1:3000", timeout=3) as response:
                if response.status < 500:
                    print("\nAIMN is running: http://localhost:3000")
                    print("Sign in with the owner email and password you created.")
                    print("Keep this computer and Docker running while using AIMN.")
                    return 0
        except (URLError, TimeoutError, OSError):
            time.sleep(3)
    print("Containers started, but the dashboard did not respond within four minutes.")
    print("Inspect logs with: docker compose logs --tail=150 api worker web")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
