from orbit.agents.ideas import IdeaAgent
from orbit.models import Idea, QualityReport
from orbit.agents.quality import QualityAgent


def test_idea_ranking_prefers_higher_score() -> None:
    low = Idea("Low", "p", "a", "h", "d", "t", {"score": 60})
    high = Idea("High", "p", "a", "h", "d", "t", {"score": 90})
    ranked = IdeaAgent().rank([low, high], minimum=0)
    assert ranked[0].title == "High"


def test_quality_gate_blocks_low_quality() -> None:
    assert not QualityAgent().approve(QualityReport(60, 60, 60, 60, 60))


def test_quality_gate_accepts_strong_report() -> None:
    assert QualityAgent().approve(QualityReport(90, 90, 90, 90, 90))
