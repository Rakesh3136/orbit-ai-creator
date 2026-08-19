from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass(frozen=True)
class PerformanceSnapshot:
    video_id: str
    views: int
    likes: int
    comments: int
    estimated_minutes_watched: float | None = None


@dataclass(frozen=True)
class StrategyRecommendation:
    area: str
    observation: str
    action: str
    confidence: float


class LearningEngine:
    """Convert observed channel metrics into bounded strategy updates."""

    def recommend(self, snapshot: PerformanceSnapshot) -> list[StrategyRecommendation]:
        recommendations: list[StrategyRecommendation] = []
        engagement = ((snapshot.likes + snapshot.comments) / snapshot.views) if snapshot.views else 0.0
        if snapshot.views < 100:
            recommendations.append(StrategyRecommendation(
                "distribution",
                "The sample is too small for a strong performance conclusion.",
                "Do not make major strategy changes; collect more data.",
                0.95,
            ))
        elif engagement < 0.02:
            recommendations.append(StrategyRecommendation(
                "audience_engagement",
                "Likes plus comments are below 2% of views.",
                "Experiment with stronger questions, sharper hooks, and more specific viewer payoffs.",
                0.78,
            ))
        else:
            recommendations.append(StrategyRecommendation(
                "audience_engagement",
                "The episode is generating meaningful visible engagement.",
                "Preserve the format and test a closely related follow-up topic.",
                0.72,
            ))
        return recommendations

    def write_strategy(self, path: str | Path, recommendations: list[StrategyRecommendation]) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps([asdict(item) for item in recommendations], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return destination
