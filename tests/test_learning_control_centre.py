from pathlib import Path

import pytest

from orbit.learning.feedback import LearningMemory, TaskEvaluation


def test_owner_review_and_approved_scoped_lessons(tmp_path: Path) -> None:
    memory = LearningMemory(tmp_path / "learning.sqlite3")
    evaluation_id = memory.record(TaskEvaluation("scriptwriter", "script", {"quality": 72}))
    review_id = memory.submit_review(
        evaluation_id, 2, correction="Opening is too generic.",
        lesson="Start with a specific surprising fact.",
        scope_type="channel", scope_id="tech-channel",
        provenance="owner:review-2026-11-04", approve_lesson=True,
    )
    assert review_id == 1
    assert memory.lessons("scriptwriter", "script") == []
    assert memory.lessons("scriptwriter", "script", channel_id="tech-channel") == [
        "Start with a specific surprising fact."
    ]
    review = memory.reviews(evaluation_id)[0]
    assert review.lesson_approved is True
    assert review.provenance == "owner:review-2026-11-04"


def test_unapproved_feedback_never_becomes_a_lesson(tmp_path: Path) -> None:
    memory = LearningMemory(tmp_path / "learning.sqlite3")
    evaluation_id = memory.record(TaskEvaluation("researcher", "research", {"accuracy": 50}))
    memory.submit_review(evaluation_id, 1, lesson="Use primary sources.")
    assert memory.lessons("researcher", "research") == []


def test_review_validation_and_unknown_evaluation(tmp_path: Path) -> None:
    memory = LearningMemory(tmp_path / "learning.sqlite3")
    with pytest.raises(ValueError):
        memory.submit_review(99, 6)
    with pytest.raises(ValueError):
        memory.submit_review(99, 4, lesson="must be approved", approve_lesson=True)
    evaluation_id = memory.record(TaskEvaluation("writer", "script", {"quality": 60}))
    with pytest.raises(ValueError):
        memory.submit_review(evaluation_id, 4, lesson="missing lesson approval", approve_lesson=True)


def test_legacy_database_gets_additive_scope_migration(tmp_path: Path) -> None:
    import sqlite3

    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT NOT NULL,
            task_type TEXT NOT NULL, overall REAL NOT NULL, passed INTEGER NOT NULL,
            scores_json TEXT NOT NULL, feedback TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )""")
    memory = LearningMemory(path)
    evaluation_id = memory.record(TaskEvaluation("writer", "script", {"quality": 70}))
    assert memory.recent()[0].id == evaluation_id
