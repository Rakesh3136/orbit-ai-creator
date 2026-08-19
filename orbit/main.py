from __future__ import annotations

import argparse
from pathlib import Path
import sys

from orbit.demo import demo_script
from orbit.pipeline import CreatorPipeline
from orbit.production.episode import EpisodeRenderer
from orbit.production.package import PublishingPackage
from orbit.production.render_plan import build_render_plan
from orbit.production.video_builder import VideoBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ORBIT creator pipeline locally.")
    parser.add_argument("topic", nargs="?", help="topic to research")
    parser.add_argument("--discover", action="store_true", help="rank candidate topics")
    parser.add_argument("--package", action="store_true", help="write a local publishing package")
    parser.add_argument("--render-title-card", action="store_true", help="render a minimal local FFmpeg title card")
    parser.add_argument("--render-video", action="store_true", help="render a complete local episode")
    parser.add_argument("--demo-video", action="store_true", help="render the deterministic demo episode without web research")
    parser.add_argument("--narration", choices=["auto", "espeak", "silent"], default="auto")
    parser.add_argument("--output", default="data/output", help="local output directory")
    args = parser.parse_args()

    output = Path(args.output)

    if args.demo_video:
        script = demo_script()
        plan = build_render_plan(script)
        rendered = EpisodeRenderer().render(
            plan,
            output / "orbit_demo.mp4",
            narration_backend=args.narration,
        )
        manifest = PublishingPackage([], "", [], [], "", "").write(
            output / "package",
            script,
            video_path=str(rendered.video_path),
            captions_path=str(rendered.captions_path),
            provenance_path=str(rendered.provenance_path),
        )
        print(f"Demo video: {rendered.video_path}")
        print(f"Captions: {rendered.captions_path}")
        print(f"Provenance: {rendered.provenance_path}")
        print(f"Publishing package: {manifest}")
        return

    pipeline = CreatorPipeline()

    if args.discover:
        topics = [
            "artificial intelligence and jobs",
            "new scientific discoveries",
            "billion-dollar technology companies",
            "future of the internet",
            "hidden infrastructure behind everyday technology",
        ]
        ideas = pipeline.discover(topics)
        print("ORBIT discovery results")
        for idea in ideas:
            print(f"{idea.score:5.1f}  {idea.title} — {idea.hook}")
        return

    topic = args.topic or "artificial intelligence and the future of work"
    result = pipeline.run(topic)
    report = result.quality
    approved = pipeline.quality_agent.approve(report)

    print(f"Topic: {result.topic}")
    print(f"Title: {result.script.title}")
    print(f"Quality: {report.overall:.1f} ({'PASS' if approved else 'BLOCK'})")

    if args.package:
        manifest = PublishingPackage("", "", [], [], "", "").write(output / "package", result.script)
        print(f"Publishing package: {manifest}")

    if args.render_title_card:
        plan = build_render_plan(result.script)
        video = VideoBuilder().build_title_card(plan.title, output / "title_card.mp4")
        print(f"Draft video: {video}")

    if args.render_video:
        plan = build_render_plan(result.script)
        rendered = EpisodeRenderer().render(
            plan,
            output / "orbit_episode.mp4",
            narration_backend=args.narration,
        )
        print(f"Episode: {rendered.video_path}")
        print(f"Captions: {rendered.captions_path}")
        print(f"Provenance: {rendered.provenance_path}")

    if report.notes:
        print("\nNOTES")
        for note in report.notes:
            print(f"- {note}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
