from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from orbit.production.render_plan import RenderPlan


class FFmpegUnavailable(RuntimeError):
    pass


class VideoBuilder:
    """Builds a simple, dependency-light draft video locally with FFmpeg.

    The builder intentionally fails clearly when FFmpeg is unavailable. It does
    not download assets or use paid services.
    """

    def __init__(self, ffmpeg: str = "ffmpeg") -> None:
        self.ffmpeg = ffmpeg

    def available(self) -> bool:
        return shutil.which(self.ffmpeg) is not None

    def build_title_card(self, title: str, output_path: str | Path, seconds: int = 8) -> Path:
        if not self.available():
            raise FFmpegUnavailable("FFmpeg is not installed or not on PATH")
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Use a plain black background so V1 has no licensing or asset problem.
        # A later visual provider can replace this adapter without changing the API.
        command = [
            self.ffmpeg,
            "-y",
            "-f", "lavfi",
            "-i", "color=c=black:s=1920x1080:r=30",
            "-t", str(seconds),
            "-vf", "format=yuv420p",
            "-an",
            str(destination),
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        return destination

    def validate(self, path: str | Path) -> bool:
        return Path(path).exists() and Path(path).stat().st_size > 0
