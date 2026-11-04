import math

import pytest

from orbit.youtube.publish_gate import decide


def test_publish_requires_human_approval() -> None:
    result = decide(quality_score=90, human_approved=False)
    assert not result.allowed


def test_publish_blocks_low_quality() -> None:
    result = decide(quality_score=74.9, human_approved=True)
    assert not result.allowed


def test_publish_accepts_approved_private_validation_package() -> None:
    result = decide(quality_score=90, human_approved=True, privacy_status="private")
    assert result.allowed


@pytest.mark.parametrize("privacy_status", ["public", "unlisted", "invalid", ""])
def test_publish_gate_rejects_every_non_private_status(privacy_status: str) -> None:
    result = decide(quality_score=90, human_approved=True, privacy_status=privacy_status)
    assert not result.allowed
    assert "private uploads only" in result.reason


@pytest.mark.parametrize("quality_score", [-0.1, 100.1, math.nan, math.inf, -math.inf])
def test_publish_gate_rejects_invalid_quality_scores(quality_score: float) -> None:
    result = decide(quality_score=quality_score, human_approved=True)
    assert not result.allowed
    assert "finite value from 0 to 100" in result.reason
