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
            human_approved=True,
        )


def test_upload_rejects_invalid_privacy_status(tmp_path: Path) -> None:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not-a-real-video")
    uploader = YouTubeUploader(credentials=None)
    with pytest.raises(ValueError, match="private-only"):
        uploader.upload(
            video,
            title="Test",
            description="Test",
            privacy_status="invalid",
            human_approved=True,
        )


@pytest.mark.parametrize("privacy_status", ["public", "unlisted"])
def test_upload_rejects_non_private_status(tmp_path: Path, privacy_status: str) -> None:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not-a-real-video")
    uploader = YouTubeUploader(credentials=None)
    with pytest.raises(ValueError, match="private-only"):
        uploader.upload(
            video,
            title="Test",
            description="Test",
            privacy_status=privacy_status,
            human_approved=True,
        )


def test_upload_requires_human_approval_even_for_private(tmp_path: Path) -> None:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not-a-real-video")
    uploader = YouTubeUploader(credentials=None)
    with pytest.raises(PermissionError):
        uploader.upload(
            video,
            title="Test",
            description="Test",
            privacy_status="private",
            human_approved=False,
        )
