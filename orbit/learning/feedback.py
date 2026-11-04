from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Iterable


@dataclass(frozen=True)
class TaskEvaluation:
    agent: str
    task_type: str
    scores: dict[str, float]
    feedback: str = ""
    approved: bool = False

    def __post_init__(self) -> None:
        if not self.agent.strip() or not self.task_type.strip():
            raise ValueError("agent and task_type must be non-empty")
        if not self.scores:
            raise ValueError("at least one score is required")
        if any(not key.strip() for key in self.scores):
            raise ValueError("score names must be non-empty")
        if any(not 0 <= value <= 100 for value in self.scores.values()):
            raise ValueError("scores must be between 0 and 100")

    @property
    def overall(self) -> float:
        return round(sum(self.scores.values()) / len(self.scores), 2)

    @property
    def passed(self) -> bool:
        return self.overall >= 80 and self.approved


@dataclass(frozen=True)
class Experience:
    id: int
    agent: str
    task_type: str
    overall: float
    passed: bool
    scores: dict[str, float]
    feedback: str
    created_at: str


class LearningMemory:
    """Local, auditable experience store. It records feedback; it does not fine-tune a model."""

    def __init__(self, path: str | Path = "data/orbit-learning.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    overall REAL NOT NULL,
                    passed INTEGER NOT NULL,
                    scores_json TEXT NOT NULL,
                    feedback TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )"""
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_experiences_agent_task "
                "ON experiences(agent, task_type, created_at)"
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def record(self, evaluation: TaskEvaluation) -> int:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            cursor = db.execute(
                """INSERT INTO experiences
                   (agent, task_type, overall, passed, scores_json, feedback, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    evaluation.agent,
                    evaluation.task_type,
                    evaluation.overall,
                    int(evaluation.passed),
                    json.dumps(evaluation.scores, sort_keys=True),
                    evaluation.feedback,
                    created_at,
                ),
            )
            return int(cursor.lastrowid)

    def recent(
        self, agent: str | None = None, task_type: str | None = None, limit: int = 20
    ) -> list[Experience]:
        if limit < 1:
            raise ValueError("limit must be positive")
        clauses: list[str] = []
        params: list[object] = []
        if agent is not None:
            clauses.append("agent = ?")
            params.append(agent)
        if task_type is not None:
            clauses.append("task_type = ?")
            params.append(task_type)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect() as db:
            rows = db.execute(
                "SELECT id, agent, task_type, overall, passed, scores_json, feedback, created_at "
                "FROM experiences" + where + " ORDER BY id DESC LIMIT ?",
                (*params, limit),
            ).fetchall()
        return [
            Experience(
                id=row[0], agent=row[1], task_type=row[2], overall=row[3],
                passed=bool(row[4]), scores=json.loads(row[5]), feedback=row[6],
                created_at=row[7],
            )
            for row in rows
        ]

    def performance(self, agent: str, task_type: str | None = None) -> dict[str, float | int]:
        clauses = ["agent = ?"]
        params: list[object] = [agent]
        if task_type is not None:
            clauses.append("task_type = ?")
            params.append(task_type)
        with self._connect() as db:
            row = db.execute(
                "SELECT COUNT(*), AVG(overall), SUM(passed) FROM experiences WHERE "
                + " AND ".join(clauses),
                params,
            ).fetchone()
        count, average, passed = row
        return {
            "tasks": int(count),
            "average_score": round(float(average or 0), 2),
            "passed": int(passed or 0),
        }

    def lessons(self, agent: str, task_type: str, limit: int = 5) -> list[str]:
        """Return recent human feedback for this agent/task, newest first."""
        return [
            item.feedback for item in self.recent(agent, task_type, limit)
            if item.feedback.strip()
        ]
