from pathlib import Path

import pytest

from orbit.learning.dashboard import serve
from orbit.learning.feedback import LearningMemory, TaskEvaluation


def test_review_queue_excludes_items_after_owner_review(tmp_path: Path) -> None:
    memory = LearningMemory(tmp_path / "learning.sqlite3")
    first = memory.record(TaskEvaluation("scriptwriter", "script", {"quality": 65}))
    second = memory.record(TaskEvaluation("researcher", "research", {"accuracy": 90}))
    assert [item.id for item in memory.review_queue()] == [second, first]
    memory.submit_review(first, 3, correction="Improve the hook.")
    assert [item.id for item in memory.review_queue()] == [second]
    assert [item.id for item in memory.review_queue(include_reviewed=True)] == [second, first]


def test_dashboard_refuses_non_loopback_bind(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="loopback"):
        serve("0.0.0.0", 8765, str(tmp_path / "learning.sqlite3"))
