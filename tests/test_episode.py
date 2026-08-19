from pathlib import Path
import shutil

import pytest

from orbit.demo import demo_script
from orbit.production.captions import write_srt
from orbit.production.episode import EpisodeRenderer
from orbit.production.render_plan import build_render_plan


def test_srt_generation_contains_scene_cues(tmp_path: Path) -> None:
    plan = build_render_plan(demo_script())
    path = write_srt(plan, tmp_path / "captions.srt")
    text = path.read_text(encoding="utf-8")
    assert "1\n00:00:00,000" in text
    assert "2\n" in text


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_episode_renderer_smoke(tmp_path: Path) -> None:
    plan = build_render_plan(demo_script())
    result = EpisodeRenderer().render(
        plan,
        tmp_path / "episode.mp4",
        narration_backend="silent",
    )
    assert result.video_path.exists()
    assert result.video_path.stat().st_size > 0
    assert result.captions_path.exists()
    assert result.provenance_path.exists()
