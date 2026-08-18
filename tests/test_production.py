from pathlib import Path

from orbit.models import Script
from orbit.production.package import PublishingPackage
from orbit.production.render_plan import build_render_plan
from orbit.production.video_builder import VideoBuilder


def sample_script() -> Script:
    return Script(
        title="A Test Story",
        hook="Here is the hook.",
        body="Here is the body.\n\nHere is another section.",
        conclusion="Here is the conclusion.",
    )


def test_render_plan_has_hook_body_and_conclusion() -> None:
    plan = build_render_plan(sample_script())
    assert len(plan.scenes) == 4
    assert plan.scenes[0].purpose == "hook"
    assert plan.scenes[-1].purpose == "conclusion"


def test_publishing_package_writes_manifest(tmp_path: Path) -> None:
    package = PublishingPackage("", "", [], [], "", "")
    manifest = package.write(tmp_path, sample_script())
    assert manifest.exists()
    assert (tmp_path / "script.txt").exists()
    assert (tmp_path / "render_plan.json").exists()


def test_video_builder_reports_ffmpeg_capability_without_running_it() -> None:
    builder = VideoBuilder()
    assert isinstance(builder.available(), bool)
