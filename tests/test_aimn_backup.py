"""Unit tests for the portable AIMN database backup helper (no Docker required)."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import aimn_backup


def test_sha256_file_streams_content(tmp_path: Path) -> None:
    target = tmp_path / "sample.bin"
    target.write_bytes(b"portable-aimn")
    assert aimn_backup.sha256_file(target) == hashlib.sha256(b"portable-aimn").hexdigest()


def test_verify_rejects_non_postgres_archive(tmp_path: Path) -> None:
    archive = tmp_path / "bad.dump"
    archive.write_bytes(b"not-a-dump")
    with pytest.raises(aimn_backup.BackupError, match="not a PostgreSQL"):
        aimn_backup.verify_archive(archive)


def test_verify_rejects_manifest_checksum_mismatch(tmp_path: Path) -> None:
    archive = tmp_path / "good.dump"
    archive.write_bytes(b"PGDMPvalid-test-data")
    manifest = archive.with_suffix(".dump.json")
    manifest.write_text(json.dumps({"sha256": "0" * 64, "size_bytes": archive.stat().st_size}))
    with pytest.raises(aimn_backup.BackupError, match="SHA-256"):
        aimn_backup.verify_archive(archive)


def test_verify_uses_postgres_to_inspect_archive(tmp_path: Path) -> None:
    archive = tmp_path / "good.dump"
    archive.write_bytes(b"PGDMPvalid-test-data")
    completed = subprocess.CompletedProcess(args=["docker"], returncode=0, stdout=b"", stderr=b"")
    with patch.object(aimn_backup, "ensure_stack_database") as ready, patch.object(
        aimn_backup.subprocess, "run", return_value=completed
    ) as run:
        result = aimn_backup.verify_archive(archive)
    ready.assert_called_once()
    assert result == {}
    assert run.call_args.kwargs["stdin"].read(5) == b"PGDMP"


def test_verify_reports_pg_restore_failure(tmp_path: Path) -> None:
    archive = tmp_path / "good.dump"
    archive.write_bytes(b"PGDMPvalid-test-data")
    completed = subprocess.CompletedProcess(args=["docker"], returncode=1, stdout=b"", stderr=b"bad archive")
    with patch.object(aimn_backup, "ensure_stack_database"), patch.object(
        aimn_backup.subprocess, "run", return_value=completed
    ):
        with pytest.raises(aimn_backup.BackupError, match="could not read"):
            aimn_backup.verify_archive(archive)
