from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PublishDecision:
    allowed: bool
    reason: str


def decide(
    *,
    quality_score: float,
    human_approved: bool,
    privacy_status: str = "private",
) -> PublishDecision:
    """Fail-closed V1 gate: only reviewed private validation uploads are allowed."""
    if privacy_status != "private":
        return PublishDecision(False, "ORBIT V1 permits private uploads only")
    if not math.isfinite(quality_score) or not 0 <= quality_score <= 100:
        return PublishDecision(False, "Quality score must be a finite value from 0 to 100")
    if quality_score < 75:
        return PublishDecision(False, "Quality score is below the publishing threshold")
    if not human_approved:
        return PublishDecision(False, "Human approval is required in V1")
    return PublishDecision(True, "Approved for private validation upload")
