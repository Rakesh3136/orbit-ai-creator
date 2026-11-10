from __future__ import annotations
import json, tarfile
from pathlib import Path
import pytest
from scripts import aimn_assets

def setup_root(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(aimn_assets, "ROOT", tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "orbit.sqlite3").write_bytes(b"memory-db")
    (tmp_path / "data" / "output").mkdir()
    (tmp_path / "data" / "output" / "episode.mp4").write_bytes(b"video")
    (tmp_path / "data" / "token.json").write_text('{"secret":"do-not-export"}')

def test_backup_and_verify_round_trip(tmp_path: Path, monkeypatch):
    setup_root(monkeypatch, tmp_path)
    target = tmp_path / "backup.tar.gz"
    aimn_assets.backup(target)
    manifest = aimn_assets.verify(target)
    assert {item["path"] for item in manifest["files"]} == {"data/orbit.sqlite3", "data/output/episode.mp4"}

def test_verify_detects_archive_tampering(tmp_path: Path, monkeypatch):
    setup_root(monkeypatch, tmp_path)
    target = tmp_path / "backup.tar.gz"
    aimn_assets.backup(target)
    target.write_bytes(target.read_bytes() + b"tampered")
    with pytest.raises(aimn_assets.AssetError, match="SHA-256"):
        aimn_assets.verify(target)

def test_verify_rejects_path_traversal(tmp_path: Path, monkeypatch):
    setup_root(monkeypatch, tmp_path)
    target = tmp_path / "bad.tar.gz"
    payload = tmp_path / "payload"; payload.write_text("unsafe")
    with tarfile.open(target, "w:gz") as tar:
        tar.add(payload, arcname="../../outside.txt")
    manifest = {"format":"aimn-assets-v1","archive_size_bytes":target.stat().st_size,
                "archive_sha256":aimn_assets.digest(target),
                "files":[{"path":"../../outside.txt","size_bytes":6,"sha256":aimn_assets.digest(payload)}]}
    aimn_assets.sidecar(target).write_text(json.dumps(manifest))
    with pytest.raises(aimn_assets.AssetError, match="Unsafe path"):
        aimn_assets.verify(target)

def test_credentials_are_excluded(tmp_path: Path, monkeypatch):
    setup_root(monkeypatch, tmp_path)
    target = tmp_path / "backup.tar.gz"; aimn_assets.backup(target)
    assert all("token.json" not in item["path"] for item in aimn_assets.verify(target)["files"])
