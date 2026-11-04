from pathlib import Path

import pytest

from orbit.learning.feedback import LearningMemory, TaskEvaluation


def test_score_and_human_approval_are_both_required(tmp_path: Path) -> None:
    evaluation = TaskEvaluation("scriptwriter", "script", {"clarity": 90, "originality": 90})
    assert evaluation.overall == 90
    assert evaluation.passed is False
    approved = TaskEvaluation(
        "scriptwriter", "script", {"clarity": 90, "originality": 90}, approved=True
    )
    assert approved.passed is True


def test_invalid_scores_are_rejected() -> None:
    with pytest.raises(ValueError):
        TaskEvaluation("researcher", "research", {"accuracy": 101})


def test_memory_persists_and_filters_experiences(tmp_path: Path) -> None:
    memory = LearningMemory(tmp_path / "learning.sqlite3")
    first = TaskEvaluation(
        "researcher", "research", {"accuracy": 70, "source_quality": 90},
        feedback="Prefer primary sources.", approved=False,
    )
    second = TaskEvaluation(
        "scriptwriter", "script", {"clarity": 95}, approved=True,
    )
    first_id = memory.record(first)
    memory.submit_review(first_id, 4, lesson="Prefer primary sources.", approve_lesson=True)
    memory.record(second)

    assert first_id == 1
    assert memory.performance("researcher") == {
        "tasks": 1, "average_score": 80.0, "passed": 0
    }
    assert memory.lessons("researcher", "research") == ["Prefer primary sources."]
    assert len(memory.recent(agent="scriptwriter")) == 1


def test_recent_rejects_non_positive_limit(tmp_path: Path) -> None:
    memory = LearningMemory(tmp_path / "learning.sqlite3")
    with pytest.raises(ValueError):
        memory.recent(limit=0)
