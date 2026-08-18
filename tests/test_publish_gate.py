from orbit.youtube.publish_gate import decide


def test_publish_requires_human_approval() -> None:
    result = decide(quality_score=90, human_approved=False)
    assert not result.allowed


def test_publish_blocks_low_quality() -> None:
    result = decide(quality_score=74.9, human_approved=True)
    assert not result.allowed


def test_publish_accepts_approved_package() -> None:
    result = decide(quality_score=90, human_approved=True, privacy_status="private")
    assert result.allowed
