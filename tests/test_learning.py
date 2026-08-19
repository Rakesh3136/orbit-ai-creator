from orbit.learning.engine import LearningEngine, PerformanceSnapshot


def test_small_sample_does_not_trigger_major_strategy_change() -> None:
    recs = LearningEngine().recommend(PerformanceSnapshot("x", 50, 1, 0))
    assert recs[0].area == "distribution"


def test_low_engagement_recommends_hook_experiments() -> None:
    recs = LearningEngine().recommend(PerformanceSnapshot("x", 1000, 5, 5))
    assert any(item.area == "audience_engagement" for item in recs)
