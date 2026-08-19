from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil
import subprocess
import textwrap

from orbit.production.captions import write_srt
from orbit.production.narration import Narrator
from orbit.production.provenance import AssetRegistry
from orbit.production.render_plan import RenderPlan


@dataclass(frozen=True)
class EpisodeRenderResult:
    video_path: Path
    captions_path: Path
    provenance_path: Path
    narration_backend: str


class EpisodeRenderer:
    """Render a complete local episode using only FFmpeg + optional local TTS."""

    def __init__(self, ffmpeg: str = "ffmpeg", narrator: Narrator | None = None) -> None:
        self.ffmpeg = ffmpeg
        self.narrator = narrator or Narrator(ffmpeg=ffmpeg)

    def _available(self) -> bool:
        return shutil.which(self.ffmpeg) is not None

    @staticmethod
    def _scene_color(number: int) -> str:
        digest = hashlib.sha1(str(number).encode()).hexdigest()[:6]
        return f"0x{digest}"

    @staticmethod
    def _wrapped(text: str, width: int = 54) -> str:
        return "\\n".join(textwrap.wrap(text.replace("%", "%%"), width=width) or [""])

    def render(
        self,
        plan: RenderPlan,
        output_path: str | Path,
        *,
        narration_backend: str = "auto",
        work_dir: str | Path | None = None,
    ) -> EpisodeRenderResult:
        if not self._available():
            raise RuntimeError("FFmpeg is not installed or not on PATH")

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        work = Path(work_dir or destination.parent / "_orbit_render")
        work.mkdir(parents=True, exist_ok=True)
        scene_files: list[Path] = []
        registry = AssetRegistry()
        narrator = Narrator(backend=narration_backend, ffmpeg=self.ffmpeg)

        for scene in plan.scenes:
            safe_name = f"scene_{scene.number:03d}"
            audio = work / f"{safe_name}.wav"
            narration = narrator.render(scene.narration, audio)
            text_file = work / f"{safe_name}.txt"
            text_file.write_text(self._wrapped(scene.narration), encoding="utf-8")
            segment = work / f"{safe_name}.mp4"

            # Use a generated background and text-only composition in V1. This is
            # deliberately copyright-safe; richer asset providers plug in later.
            fontfile = None
            for candidate in [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
                "C:/Windows/Fonts/arial.ttf",
            ]:
                if Path(candidate).exists():
                    fontfile = candidate
                    break
            draw = (
                f"drawtext=textfile='{text_file.as_posix()}':fontcolor=white:fontsize=48:"
                "x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.30:boxborderw=28"
            )
            if fontfile:
                draw = draw.replace("drawtext=textfile=", f"drawtext=fontfile='{fontfile}':textfile=")

            subprocess.run(
                [
                    self.ffmpeg, "-y",
                    "-f", "lavfi", "-i", f"color=c={self._scene_color(scene.number)}:s=1920x1080:r=30",
                    "-i", str(audio),
                    "-vf", f"format=yuv420p,{draw}",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(segment),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            scene_files.append(segment)
            registry.add(audio, asset_type="narration", source=f"local:{narration.backend}", license="free/local")
            registry.add(segment, asset_type="scene-video", source="generated:orbit", license="self-generated")

        concat_file = work / "concat.txt"
        concat_file.write_text("\n".join(f"file '{p.as_posix()}'" for p in scene_files), encoding="utf-8")
        subprocess.run(
            [self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(destination)],
            check=True,
            capture_output=True,
            text=True,
        )

        captions = write_srt(plan, destination.with_suffix(".srt"))
        provenance = registry.write(destination.with_name("asset_provenance.json"))
        return EpisodeRenderResult(destination, captions, provenance, narration.backend)
