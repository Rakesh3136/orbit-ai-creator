from __future__ import annotations

import argparse
from pathlib import Path

from orbit.pipeline import CreatorPipeline
from orbit.production.package import PublishingPackage
from orbit.production.render_plan import build_render_plan
from orbit.production.video_builder import VideoBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ORBIT creator pipeline locally.")
    parser.add_argument("topic", nargs="?", help="topic to research")
    parser.add_argument("--discover", action="store_true", help="rank candidate topics")
    parser.add_argument("--package", action="store_true", help="write a local publishing package")
    parser.add_argument("--render-title-card", action="store_true", help="render a minimal local FFmpeg title card")
    parser.add_argument("--output", default="data/output", help="local output directory")
    args = parser.parse_args()

    pipeline = CreatorPipeline()
    output = Path(args.output)

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

    if report.notes:
        print("\nNOTES")
        for note in report.notes:
            print(f"- {note}")


if __name__ == "__main__":
    main()
