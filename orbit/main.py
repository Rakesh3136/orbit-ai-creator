from __future__ import annotations

import argparse

from orbit.pipeline import CreatorPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ORBIT creator pipeline locally.")
    parser.add_argument("topic", nargs="?", help="topic to research")
    parser.add_argument("--discover", action="store_true", help="rank candidate topics instead of writing a script")
    args = parser.parse_args()

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
    print("\nHOOK\n" + result.script.hook)
    print("\nBODY\n" + result.script.body)
    print("\nCONCLUSION\n" + result.script.conclusion)
    if report.notes:
        print("\nNOTES")
        for note in report.notes:
            print(f"- {note}")


if __name__ == "__main__":
    main()
