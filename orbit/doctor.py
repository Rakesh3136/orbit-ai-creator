from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import urllib.request


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_checks() -> list[Check]:
    checks = [
        Check("python", True, os.sys.version.split()[0]),
        Check("ffmpeg", shutil.which("ffmpeg") is not None, shutil.which("ffmpeg") or "not found"),
        Check("espeak", bool(shutil.which("espeak-ng") or shutil.which("espeak")), shutil.which("espeak-ng") or shutil.which("espeak") or "not found"),
    ]
    provider = os.getenv("ORBIT_LLM_PROVIDER", "deterministic")
    if provider == "ollama":
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as response:
                checks.append(Check("ollama", response.status == 200, "local server reachable"))
        except Exception:
            checks.append(Check("ollama", False, "ORBIT_LLM_PROVIDER=ollama but local server is unreachable"))
    else:
        checks.append(Check("llm", True, "deterministic provider"))
    checks.append(Check("youtube_credentials", bool(os.getenv("YOUTUBE_CLIENT_ID")), "configured" if os.getenv("YOUTUBE_CLIENT_ID") else "not configured (optional until upload stage)"))
    return checks


def main() -> int:
    checks = run_checks()
    for check in checks:
        print(f"{'PASS' if check.ok else 'WARN':4} {check.name:20} {check.detail}")
    required = {"python", "ffmpeg"}
    return 0 if all(check.ok for check in checks if check.name in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
