from pathlib import Path

import pytest

from orbit.youtube.uploader import YouTubeUploader


def test_upload_requires_human_approval(tmp_path: Path) -> None:
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"sample")
    uploader = YouTubeUploader(credentials=None)
    with pytest.raises(PermissionError):
        uploader.upload(video, title="Test", description="Test")
