from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoMetrics:
    video_id: str
    views: int
    likes: int
    comments: int
    estimated_minutes_watched: float | None = None


class YouTubeAnalytics:
    """Optional read-only analytics adapter for the authenticated channel."""

    def __init__(self, credentials) -> None:
        self.credentials = credentials

    def get_video(self, video_id: str) -> VideoMetrics:
        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Install the optional YouTube dependencies with pip install '.[youtube]'."
            ) from exc
        service = build("youtube", "v3", credentials=self.credentials)
        response = service.videos().list(part="statistics", id=video_id).execute()
        items = response.get("items", [])
        if not items:
            raise ValueError(f"Video not found: {video_id}")
        stats = items[0]["statistics"]
        return VideoMetrics(
            video_id=video_id,
            views=int(stats.get("viewCount", 0)),
            likes=int(stats.get("likeCount", 0)),
            comments=int(stats.get("commentCount", 0)),
        )
