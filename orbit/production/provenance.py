from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class AssetRecord:
    path: str
    sha256: str
    asset_type: str
    source: str
    license: str
    notes: str = ""


class AssetRegistry:
    """Track the origin and integrity of production assets."""

    def __init__(self) -> None:
        self.records: list[AssetRecord] = []

    def add(self, path: str | Path, *, asset_type: str, source: str, license: str, notes: str = "") -> AssetRecord:
        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(file_path)
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        record = AssetRecord(str(file_path), digest, asset_type, source, license, notes)
        self.records.append(record)
        return record

    def write(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps([asdict(record) for record in self.records], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return destination
