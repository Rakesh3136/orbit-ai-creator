from __future__ import annotations

import sqlite3
from pathlib import Path


class MemoryStore:
    """Tiny local memory layer; intentionally dependency-free for the $0 bootstrap."""

    def __init__(self, path: str = "data/orbit.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init(self):
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )

    def remember(self, kind: str, payload: str) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO events(kind, payload) VALUES (?, ?)", (kind, payload))
