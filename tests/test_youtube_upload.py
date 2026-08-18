from pathlib import Path

import pytest

from orbit.youtube.uploader import YouTubeUploader


def test_upload_rejects_missing_video_before_provider_call(tmp_path: Path) -> None:
    uploader = YouTubeUploader(credentials=None)
    with pytest.raises(FileNotFoundError):
        uploader.upload(
            tmp_path / "missing.mp4",
            title="Test",
            description="Test",
            privacy_status="private",
        )


def test_upload_rejects_invalid_privacy_status(tmp_path: Path) -> None:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not-a-real-video")
    uploader = YouTubeUploader(credentials=None)
    with pytest.raises(ValueError):
        uploader.upload(
            video,
            title="Test",
            description="Test",
            privacy_status="invalid",
        )
