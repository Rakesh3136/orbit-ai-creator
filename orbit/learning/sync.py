from __future__ import annotations

from pathlib import Path

from orbit.learning.engine import LearningEngine, PerformanceSnapshot
from orbit.youtube.analytics import YouTubeAnalytics


def sync_video(
    analytics: YouTubeAnalytics,
    video_id: str,
    output_path: str | Path,
) -> Path:
    metrics = analytics.get_video(video_id)
    snapshot = PerformanceSnapshot(
        video_id=metrics.video_id,
        views=metrics.views,
        likes=metrics.likes,
        comments=metrics.comments,
        estimated_minutes_watched=metrics.estimated_minutes_watched,
    )
    recommendations = LearningEngine().recommend(snapshot)
    return LearningEngine().write_strategy(output_path, recommendations)
