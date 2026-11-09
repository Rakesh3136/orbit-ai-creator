#!/usr/bin/env python3
"""Portable, verified PostgreSQL backup/restore helper for the AIMN Compose stack."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKUP_DIR = ROOT / "backups"
COMPOSE = ["docker", "compose"]
SERVICES_TO_PAUSE = ["api", "worker", "web"]


class BackupError(RuntimeError):
    pass


def run(command: list[str], *, stdout=None, check: bool = True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError as exc:
        raise BackupError("Docker CLI was not found. Install Docker Desktop/Engine and Compose.") from exc
    if check and result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise BackupError(detail or f"Command failed with exit code {result.returncode}: {' '.join(command)}")
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compose(*args: str, stdout=None, check: bool = True):
    return run(COMPOSE + list(args), stdout=stdout, check=check)


def ensure_stack_database() -> None:
    compose("ps", "--status", "running", "postgres")
    result = compose("exec", "-T", "postgres", "pg_isready", "-U", "aimn", "-d", "aimn", check=False)
    if result.returncode:
        raise BackupError("AIMN PostgreSQL is not ready. Start it with: docker compose up -d postgres")


def backup(destination: Path) -> Path:
    ensure_stack_database()
    destination = destination.expanduser()
    if not destination.is_absolute():
        destination = ROOT / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.with_suffix(destination.suffix + ".json").exists():
        raise BackupError(f"Refusing to overwrite an existing backup: {destination}")

    fd, temp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".partial", dir=destination.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        with temp.open("wb") as output:
            compose("exec", "-T", "postgres", "pg_dump", "-U", "aimn", "-d", "aimn", "-Fc", stdout=output)
        with temp.open("rb") as check_stream:
            signature = check_stream.read(5)
        if temp.stat().st_size < 5 or signature != b"PGDMP":
            raise BackupError("pg_dump output is not a valid PostgreSQL custom-format archive.")
        checksum = sha256_file(temp)
        size = temp.stat().st_size
        temp.replace(destination)
        manifest = {
            "format": "postgresql-custom",
            "database": "aimn",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "file": destination.name,
            "size_bytes": size,
            "sha256": checksum,
        }
        manifest_path = destination.with_suffix(destination.suffix + ".json")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        try:
            os.chmod(manifest_path, 0o600)
            os.chmod(destination, 0o600)
        except OSError:
            pass
        return destination
    finally:
        if temp.exists():
            temp.unlink()


def verify_archive(archive: Path) -> dict:
    archive = archive.expanduser().resolve()
    if not archive.is_file():
        raise BackupError(f"Backup file does not exist: {archive}")
    with archive.open("rb") as stream:
        if stream.read(5) != b"PGDMP":
            raise BackupError("This file is not a PostgreSQL custom-format backup.")
    manifest_path = archive.with_suffix(archive.suffix + ".json")
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BackupError("Backup manifest is unreadable or invalid.") from exc
        actual = sha256_file(archive)
        if manifest.get("sha256") != actual:
            raise BackupError("Backup SHA-256 does not match its manifest. Do not restore this file.")
        if manifest.get("size_bytes") != archive.stat().st_size:
            raise BackupError("Backup size does not match its manifest. Do not restore this file.")
    # pg_restore reads the custom-format archive from stdin when no filename is supplied.
    ensure_stack_database()
    with archive.open("rb") as source:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "pg_restore", "--list"],
            cwd=ROOT, stdin=source, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False,
        )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise BackupError("PostgreSQL could not read this archive. " + detail)
    return manifest


def restore(archive: Path, confirm_replace: bool) -> None:
    archive = archive.expanduser().resolve()
    if not confirm_replace:
        raise BackupError("Restore is destructive. Re-run with --confirm-replace after checking the target database.")
    if not sys.stdin.isatty():
        raise BackupError("Interactive confirmation is required. Run this command in a terminal.")
    print(f"Target database: aimn (Docker Compose service: postgres)")
    print(f"Backup file: {archive}")
    answer = input("This replaces matching database objects. Type RESTORE AIMN to continue: ").strip()
    if answer != "RESTORE AIMN":
        raise BackupError("Confirmation did not match. Nothing was restored.")

    ensure_stack_database()
    verify_archive(archive)
    compose("stop", *SERVICES_TO_PAUSE)
    try:
        with archive.open("rb") as source:
            result = subprocess.run(
                COMPOSE + ["exec", "-T", "postgres", "pg_restore", "-U", "aimn", "-d", "aimn",
                           "--no-owner", "--no-privileges", "--clean", "--if-exists", "--exit-on-error"],
                cwd=ROOT, stdin=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
        if result.returncode:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise BackupError("Restore failed: " + (detail or f"exit code {result.returncode}"))
    finally:
        compose("up", "-d", *SERVICES_TO_PAUSE)
    print("Database restore completed. Check AIMN login, networks, channels, tasks and agent lessons.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create and verify portable AIMN PostgreSQL backups.")
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("backup", help="Create a timestamped backup and SHA-256 manifest.")
    make.add_argument("--output", type=Path, help="Output .dump path (default: backups/aimn-UTC_TIMESTAMP.dump).")
    check = sub.add_parser("verify", help="Verify a backup archive and its optional SHA-256 manifest.")
    check.add_argument("archive", type=Path)
    put = sub.add_parser("restore", help="Restore a backup after explicit destructive confirmation.")
    put.add_argument("archive", type=Path)
    put.add_argument("--confirm-replace", action="store_true", help="Acknowledge that the target database will be changed.")
    args = parser.parse_args(argv)

    try:
        if args.command == "backup":
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            path = args.output or (DEFAULT_BACKUP_DIR / f"aimn-{stamp}.dump")
            created = backup(path)
            print(f"Backup created: {created}")
            print(f"Manifest: {created.with_suffix(created.suffix + '.json')}")
            print("Keep the private .env file separately in encrypted storage; it is not included.")
        elif args.command == "verify":
            meta = verify_archive(args.archive)
            print(f"Backup verified: {args.archive.resolve()}")
            print(f"SHA-256: {sha256_file(args.archive.resolve())}")
            if not meta:
                print("No manifest found; archive format was checked, but no saved checksum was available.")
        else:
            restore(args.archive, args.confirm_replace)
        return 0
    except BackupError as exc:
        print(f"AIMN backup error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
