#!/usr/bin/env python3
"""Portable archive for ORBIT's local memory and generated assets (no Docker required)."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, tarfile, tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "backups"
INCLUDE_DIRS = ("data", "media/raw", "media/generated", "media/final")
EXCLUDED_NAMES = {".env", "credentials.json", "token.json"}
EXCLUDED_PREFIXES = ("client_secret",)
CHUNK = 1024 * 1024

class AssetError(RuntimeError):
    pass

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()

def allowed_file(path: Path) -> bool:
    name = path.name.lower()
    return name not in EXCLUDED_NAMES and not any(name.startswith(p) for p in EXCLUDED_PREFIXES)

def collect_files() -> list[Path]:
    files = []
    for relative in INCLUDE_DIRS:
        base = ROOT / relative
        if not base.exists():
            continue
        if base.is_symlink() or not base.is_dir():
            raise AssetError(f"Refusing unsafe asset directory: {relative}")
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                continue
            if path.is_file() and allowed_file(path):
                files.append(path)
    return files

def sidecar(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".json")

def backup(destination: Path) -> Path:
    destination = destination.expanduser()
    if not destination.is_absolute():
        destination = ROOT / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or sidecar(destination).exists():
        raise AssetError(f"Refusing to overwrite existing archive: {destination}")
    files = collect_files()
    fd, temp_name = tempfile.mkstemp(prefix=destination.name + ".", suffix=".partial", dir=destination.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        entries = []
        with tarfile.open(temp, "w:gz") as archive:
            for path in files:
                relative = path.relative_to(ROOT).as_posix()
                archive.add(path, arcname=relative, recursive=False)
                entries.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": digest(path)})
        archive_hash, archive_size = digest(temp), temp.stat().st_size
        temp.replace(destination)
        metadata = {"format":"aimn-assets-v1","created_at":datetime.now(timezone.utc).isoformat(),
                    "archive":destination.name,"archive_size_bytes":archive_size,
                    "archive_sha256":archive_hash,"files":entries}
        sidecar(destination).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        try:
            os.chmod(destination, 0o600)
            os.chmod(sidecar(destination), 0o600)
        except OSError:
            pass
        return destination
    finally:
        if temp.exists():
            temp.unlink()

def _safe_member_name(name: str) -> PurePosixPath:
    member = PurePosixPath(name)
    if member.is_absolute() or not member.parts or any(p in ("", ".", "..") for p in member.parts):
        raise AssetError(f"Unsafe path in asset archive: {name}")
    if not any(name == root or name.startswith(root + "/") for root in ("data", "media")):
        raise AssetError(f"Unexpected path in asset archive: {name}")
    base = member.name.lower()
    if base in EXCLUDED_NAMES or any(base.startswith(p) for p in EXCLUDED_PREFIXES):
        raise AssetError(f"Credential-like file is not allowed in asset archive: {name}")
    return member

def verify(archive_path: Path) -> dict:
    archive_path = archive_path.expanduser().resolve()
    if not archive_path.is_file():
        raise AssetError(f"Asset archive does not exist: {archive_path}")
    manifest_path = sidecar(archive_path)
    if not manifest_path.is_file():
        raise AssetError("Asset archive manifest is missing; refusing to restore an unverified archive.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssetError("Asset archive manifest is invalid.") from exc
    if manifest.get("format") != "aimn-assets-v1":
        raise AssetError("Unsupported asset archive manifest format.")
    if manifest.get("archive_sha256") != digest(archive_path):
        raise AssetError("Asset archive SHA-256 does not match its manifest.")
    if manifest.get("archive_size_bytes") != archive_path.stat().st_size:
        raise AssetError("Asset archive size does not match its manifest.")
    expected = {item["path"]: item for item in manifest.get("files", [])}
    seen = set()
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            for item in tar:
                _safe_member_name(item.name)
                if item.isdir():
                    continue
                if not item.isfile():
                    raise AssetError(f"Unsupported non-file entry in archive: {item.name}")
                if item.name in seen or item.name not in expected:
                    raise AssetError(f"Unexpected or duplicate file in archive: {item.name}")
                source = tar.extractfile(item)
                if source is None:
                    raise AssetError(f"Could not read archive entry: {item.name}")
                h, size = hashlib.sha256(), 0
                while True:
                    chunk = source.read(CHUNK)
                    if not chunk: break
                    size += len(chunk); h.update(chunk)
                info = expected[item.name]
                if size != info.get("size_bytes") or h.hexdigest() != info.get("sha256"):
                    raise AssetError(f"File checksum mismatch inside archive: {item.name}")
                seen.add(item.name)
    except (tarfile.TarError, OSError) as exc:
        raise AssetError(f"Could not read asset archive: {exc}") from exc
    if seen != set(expected):
        raise AssetError("Archive contents do not match the manifest.")
    return manifest

def restore(archive_path: Path, confirm: bool) -> None:
    if not confirm:
        raise AssetError("Restore can add files to your working data. Re-run with --confirm-add.")
    if not sys.stdin.isatty():
        raise AssetError("Interactive confirmation is required. Run this command in a terminal.")
    archive_path = archive_path.expanduser().resolve()
    manifest = verify(archive_path)
    print(f"Files to restore: {len(manifest['files'])}")
    if input("This adds files and never overwrites existing files. Type RESTORE AIMN ASSETS: ").strip() != "RESTORE AIMN ASSETS":
        raise AssetError("Confirmation did not match. Nothing was restored.")
    destinations = []
    for item in manifest["files"]:
        relative = _safe_member_name(item["path"])
        target = ROOT.joinpath(*relative.parts)
        current = ROOT
        for part in relative.parts[:-1]:
            current = current / part
            if current.exists() and (current.is_symlink() or not current.is_dir()):
                raise AssetError(f"Unsafe existing destination directory: {current}")
        if target.exists() or target.is_symlink():
            raise AssetError(f"Refusing to overwrite existing file: {target}")
        destinations.append((relative, target))
    with tarfile.open(archive_path, "r:gz") as tar:
        members = {item.name:item for item in tar if item.isfile()}
        for relative, target in destinations:
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(members[relative.as_posix()])
            if source is None: raise AssetError(f"Could not read archive entry: {relative}")
            with source, target.open("xb") as output:
                while True:
                    chunk = source.read(CHUNK)
                    if not chunk: break
                    output.write(chunk)
    print("Asset restore completed. Existing files were not overwritten.")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Back up and restore ORBIT local memory and generated assets.")
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("backup"); make.add_argument("--output", type=Path)
    check = commands.add_parser("verify"); check.add_argument("archive", type=Path)
    put = commands.add_parser("restore"); put.add_argument("archive", type=Path); put.add_argument("--confirm-add", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "backup":
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            path = args.output or (BACKUP_DIR / f"aimn-assets-{stamp}.tar.gz")
            created = backup(path)
            print(f"Asset archive created: {created}")
            print(f"Manifest: {sidecar(created)}")
        elif args.command == "verify":
            meta = verify(args.archive); print(f"Asset archive verified: {args.archive.resolve()} ({len(meta['files'])} files)")
        else:
            restore(args.archive, args.confirm_add)
        return 0
    except AssetError as exc:
        print(f"AIMN asset error: {exc}", file=sys.stderr); return 2

if __name__ == "__main__":
    raise SystemExit(main())
