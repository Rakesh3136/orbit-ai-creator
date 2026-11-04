from pathlib import Path

from orbit.learning.feedback import LearningMemory, TaskEvaluation
from orbit.memory import MemoryStore
from orbit.pipeline import CreatorPipeline


def test_pipeline_loads_human_lessons_and_records_unapproved_evaluation(tmp_path: Path) -> None:
    learning = LearningMemory(tmp_path / "learning.sqlite3")
    evaluation_id = learning.record(
        TaskEvaluation(
            agent="scriptwriter",
            task_type="script",
            scores={"clarity": 72},
            approved=False,
        )
    )
    learning.submit_review(
        evaluation_id, 4,
        lesson="Open with a concrete viewer question.",
        approve_lesson=True,
    )
    pipeline = CreatorPipeline(
        memory=MemoryStore(str(tmp_path / "memory.sqlite3")),
        learning_memory=learning,
    )
    pipeline.research.search = lambda topic, limit=8: []
    result = pipeline.run("renewable energy")

    assert result.lessons_considered == ("Open with a concrete viewer question.",)
    assert result.evaluation_id is not None
    assert result.quality.notes
    assert learning.performance("scriptwriter", "script")["tasks"] == 2
    newest = learning.recent(agent="scriptwriter", task_type="script", limit=1)[0]
    assert newest.passed is False
    assert newest.feedback == ""


def test_pipeline_does_not_mark_work_human_approved(tmp_path: Path) -> None:
    learning = LearningMemory(tmp_path / "learning.sqlite3")
    pipeline = CreatorPipeline(
        memory=MemoryStore(str(tmp_path / "memory.sqlite3")),
        learning_memory=learning,
    )
    pipeline.research.search = lambda topic, limit=8: []
    result = pipeline.run("clean energy")

    assert result.evaluation_id == 1
    assert learning.recent(limit=1)[0].passed is False
