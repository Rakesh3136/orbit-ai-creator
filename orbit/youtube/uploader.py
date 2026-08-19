from __future__ import annotations

from pathlib import Path

UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"


class YouTubeUploader:
    """Thin adapter around YouTube Data API v3 videos.insert.

    V1 requires explicit human approval at the adapter boundary. Credentials
    never imply permission to publish.
    """

    def __init__(self, credentials) -> None:
        self.credentials = credentials

    def upload(
        self,
        video_path: str | Path,
        title: str,
        description: str,
        tags: list[str] | None = None,
        privacy_status: str = "private",
        *,
        human_approved: bool = False,
    ) -> str:
        if not human_approved:
            raise PermissionError("Human approval is required before any YouTube upload in V1")
        if privacy_status not in {"private", "unlisted", "public"}:
            raise ValueError("privacy_status must be private, unlisted, or public")
        path = Path(video_path)
        if not path.exists() or path.stat().st_size == 0:
            raise FileNotFoundError(path)

        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise RuntimeError(
                "Install the optional YouTube dependencies with "
                "pip install '.[youtube]' before uploading."
            ) from exc

        service = build("youtube", "v3", credentials=self.credentials)
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": (tags or [])[:500],
                "categoryId": "27",
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }
        request = service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(str(path), chunksize=-1, resumable=True, mimetype="video/*"),
        )
        response = request.execute()
        return str(response["id"])
