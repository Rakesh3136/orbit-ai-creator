from __future__ import annotations

from pathlib import Path
import json

from orbit.pipeline import CreatorPipeline


DEFAULT_TOPICS = [
    "artificial intelligence and jobs",
    "new scientific discoveries",
    "billion-dollar technology companies",
    "future of the internet",
    "hidden infrastructure behind everyday technology",
    "digital culture and the future",
]


def run_discovery(output_dir: str | Path = "data/discovery", topics: list[str] | None = None) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    ideas = CreatorPipeline().discover(topics or DEFAULT_TOPICS)
    payload = [
        {
            "title": idea.title,
            "premise": idea.premise,
            "audience": idea.audience,
            "hook": idea.hook,
            "differentiator": idea.differentiator,
            "topic": idea.topic,
            "score": idea.score,
            "scores": idea.scores,
        }
        for idea in ideas
    ]
    path = output / "ideas.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
