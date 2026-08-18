from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublishDecision:
    allowed: bool
    reason: str


def decide(*, quality_score: float, human_approved: bool, privacy_status: str = "private") -> PublishDecision:
    if privacy_status not in {"private", "unlisted", "public"}:
        return PublishDecision(False, "Invalid privacy status")
    if quality_score < 75:
        return PublishDecision(False, "Quality score is below the publishing threshold")
    if not human_approved:
        return PublishDecision(False, "Human approval is required in V1")
    return PublishDecision(True, "Approved for upload")
