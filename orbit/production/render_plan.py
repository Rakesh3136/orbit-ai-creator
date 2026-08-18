from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from orbit.models import Script


@dataclass(frozen=True)
class Scene:
    number: int
    purpose: str
    narration: str
    visual_direction: str
    duration_seconds: int


@dataclass(frozen=True)
class RenderPlan:
    title: str
    scenes: list[Scene]

    def write_json(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                {"title": self.title, "scenes": [asdict(scene) for scene in self.scenes]},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return destination


def build_render_plan(script: Script) -> RenderPlan:
    body_chunks = [chunk.strip() for chunk in script.body.split("\n\n") if chunk.strip()]
    scenes: list[Scene] = [
        Scene(1, "hook", script.hook, "Opening title card with subtle motion; no misleading imagery.", 12),
    ]
    for index, chunk in enumerate(body_chunks, start=2):
        scenes.append(
            Scene(
                index,
                "story",
                chunk,
                "Use original diagrams, licensed/public-domain assets, screenshots with permission, or generated visuals.",
                max(12, min(35, len(chunk) // 7)),
            )
        )
    scenes.append(
        Scene(len(scenes) + 1, "conclusion", script.conclusion, "End card with channel identity and a simple viewer question.", 15)
    )
    return RenderPlan(script.title, scenes)
