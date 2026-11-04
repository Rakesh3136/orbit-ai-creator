from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3


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
        if not self.scores or any(not key.strip() for key in self.scores):
            raise ValueError("at least one named score is required")
        if any(not isinstance(value, (int, float)) or not 0 <= value <= 100 for value in self.scores.values()):
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


@dataclass(frozen=True)
class HumanReview:
    id: int
    evaluation_id: int
    rating: int
    correction: str
    lesson: str
    scope_type: str
    scope_id: str
    provenance: str
    lesson_approved: bool
    created_at: str


class LearningMemory:
    """Local auditable feedback store; it records experience but never fine-tunes a model."""

    def __init__(self, path: str | Path = "data/orbit-learning.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT NOT NULL, task_type TEXT NOT NULL, overall REAL NOT NULL,
                passed INTEGER NOT NULL, scores_json TEXT NOT NULL,
                feedback TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_experiences_agent_task ON experiences(agent, task_type, created_at)")
            # Additive migration keeps existing local databases usable.
            columns = {row[1] for row in db.execute("PRAGMA table_info(experiences)")}
            for name, declaration in (
                ("network_id", "TEXT NOT NULL DEFAULT 'default'"),
                ("channel_id", "TEXT NOT NULL DEFAULT ''"),
                ("provenance", "TEXT NOT NULL DEFAULT 'pipeline:auto-score'"),
            ):
                if name not in columns:
                    db.execute(f"ALTER TABLE experiences ADD COLUMN {name} {declaration}")
            db.execute("""CREATE TABLE IF NOT EXISTS human_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id INTEGER NOT NULL REFERENCES experiences(id),
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                correction TEXT NOT NULL DEFAULT '',
                lesson TEXT NOT NULL DEFAULT '',
                scope_type TEXT NOT NULL CHECK(scope_type IN ('network','channel')),
                scope_id TEXT NOT NULL,
                provenance TEXT NOT NULL,
                lesson_approved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_reviews_evaluation ON human_reviews(evaluation_id)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_reviews_scope ON human_reviews(scope_type, scope_id, lesson_approved)")

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def record(self, evaluation: TaskEvaluation, network_id: str = "default", channel_id: str = "", provenance: str = "pipeline:auto-score") -> int:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            cursor = db.execute(
                """INSERT INTO experiences
                (agent, task_type, overall, passed, scores_json, feedback, created_at, network_id, channel_id, provenance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (evaluation.agent, evaluation.task_type, evaluation.overall, int(evaluation.passed),
                 json.dumps(evaluation.scores, sort_keys=True), evaluation.feedback, created_at,
                 network_id, channel_id, provenance),
            )
            return int(cursor.lastrowid)

    def recent(self, agent: str | None = None, task_type: str | None = None, limit: int = 20) -> list[Experience]:
        if limit < 1:
            raise ValueError("limit must be positive")
        clauses, params = [], []
        if agent is not None:
            clauses.append("agent = ?"); params.append(agent)
        if task_type is not None:
            clauses.append("task_type = ?"); params.append(task_type)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with self._connect() as db:
            rows = db.execute("SELECT id, agent, task_type, overall, passed, scores_json, feedback, created_at FROM experiences" + where + " ORDER BY id DESC LIMIT ?", (*params, limit)).fetchall()
        return [Experience(row["id"], row["agent"], row["task_type"], row["overall"], bool(row["passed"]), json.loads(row["scores_json"]), row["feedback"], row["created_at"]) for row in rows]

    def performance(self, agent: str, task_type: str | None = None) -> dict[str, float | int]:
        clauses, params = ["agent = ?"], [agent]
        if task_type is not None:
            clauses.append("task_type = ?"); params.append(task_type)
        with self._connect() as db:
            row = db.execute("SELECT COUNT(*), AVG(overall), SUM(passed) FROM experiences WHERE " + " AND ".join(clauses), params).fetchone()
        return {"tasks": int(row[0]), "average_score": round(float(row[1] or 0), 2), "passed": int(row[2] or 0)}

    def submit_review(
        self, evaluation_id: int, rating: int, correction: str = "", lesson: str = "",
        scope_type: str = "network", scope_id: str = "default",
        provenance: str = "owner:cli-review", approve_lesson: bool = False,
    ) -> int:
        if not 1 <= rating <= 5:
            raise ValueError("rating must be between 1 and 5")
        if scope_type not in {"network", "channel"}:
            raise ValueError("scope_type must be 'network' or 'channel'")
        if not scope_id.strip() or not provenance.strip():
            raise ValueError("scope_id and provenance must be non-empty")
        if approve_lesson and not lesson.strip():
            raise ValueError("an approved lesson must contain text")
        if approve_lesson and not correction.strip() and not lesson.strip():
            raise ValueError("approval requires a correction or lesson")
        with self._connect() as db:
            if db.execute("SELECT 1 FROM experiences WHERE id = ?", (evaluation_id,)).fetchone() is None:
                raise ValueError(f"evaluation {evaluation_id} does not exist")
            cursor = db.execute(
                """INSERT INTO human_reviews
                (evaluation_id, rating, correction, lesson, scope_type, scope_id, provenance, lesson_approved, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (evaluation_id, rating, correction, lesson, scope_type, scope_id, provenance,
                 int(approve_lesson), datetime.now(timezone.utc).isoformat()),
            )
            return int(cursor.lastrowid)

    def reviews(self, evaluation_id: int | None = None, limit: int = 50) -> list[HumanReview]:
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._connect() as db:
            if evaluation_id is None:
                rows = db.execute("SELECT * FROM human_reviews ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM human_reviews WHERE evaluation_id = ? ORDER BY id DESC LIMIT ?", (evaluation_id, limit)).fetchall()
        return [HumanReview(row["id"], row["evaluation_id"], row["rating"], row["correction"], row["lesson"], row["scope_type"], row["scope_id"], row["provenance"], bool(row["lesson_approved"]), row["created_at"]) for row in rows]

    def lessons(self, agent: str, task_type: str, limit: int = 5, network_id: str = "default", channel_id: str = "") -> list[str]:
        """Only owner-approved lessons with matching network/channel scope are reusable."""
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._connect() as db:
            rows = db.execute(
                """SELECT r.lesson FROM human_reviews r
                JOIN experiences e ON e.id = r.evaluation_id
                WHERE e.agent = ? AND e.task_type = ? AND r.lesson_approved = 1
                AND ((r.scope_type = 'network' AND r.scope_id = ?)
                     OR (r.scope_type = 'channel' AND r.scope_id = ?))
                AND r.lesson <> '' ORDER BY r.id DESC LIMIT ?""",
                (agent, task_type, network_id, channel_id, limit),
            ).fetchall()
        return [row["lesson"] for row in rows]
