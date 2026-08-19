from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class NarrationResult:
    path: Path
    backend: str
    duration_seconds: float


class Narrator:
    """Free/local narration with an explicit silent fallback.

    Preferred backend is espeak-ng, which is free and can be installed locally.
    The silent backend exists so CI and machines without TTS can still render a
    structurally valid episode. A silent render is never considered publish-ready
    by the quality gate.
    """

    def __init__(self, backend: str = "auto", ffmpeg: str = "ffmpeg") -> None:
        self.backend = backend
        self.ffmpeg = ffmpeg

    def _espeak_binary(self) -> str | None:
        return shutil.which("espeak-ng") or shutil.which("espeak")

    def available(self, backend: str | None = None) -> bool:
        choice = backend or self.backend
        if choice == "silent":
            return shutil.which(self.ffmpeg) is not None
        if choice in {"auto", "espeak", "espeak-ng"}:
            return self._espeak_binary() is not None or shutil.which(self.ffmpeg) is not None
        return False

    @staticmethod
    def _estimate_duration(text: str) -> float:
        words = max(1, len(text.split()))
        return max(1.5, words / 2.4)

    def _silent(self, text: str, output: Path) -> NarrationResult:
        duration = self._estimate_duration(text)
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                self.ffmpeg, "-y", "-f", "lavfi",
                "-i", "anullsrc=r=22050:cl=mono",
                "-t", f"{duration:.2f}", "-c:a", "pcm_s16le", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return NarrationResult(output, "silent", duration)

    def render(self, text: str, output: str | Path) -> NarrationResult:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        choice = self.backend
        binary = self._espeak_binary()

        if choice == "silent" or (choice == "auto" and binary is None):
            return self._silent(text, destination)
        if choice in {"auto", "espeak", "espeak-ng"} and binary:
            subprocess.run(
                [binary, "-w", str(destination), "-s", "155", "-v", "en-us", text],
                check=True,
                capture_output=True,
                text=True,
            )
            # Ask ffmpeg for the actual duration so the renderer can synchronize.
            probe = subprocess.run(
                [self.ffmpeg, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(destination)],
                check=True,
                capture_output=True,
                text=True,
            )
            return NarrationResult(destination, "espeak", float(probe.stdout.strip()))

        raise RuntimeError(f"Unsupported or unavailable narration backend: {choice}")
