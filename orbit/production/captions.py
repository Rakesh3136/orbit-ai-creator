from __future__ import annotations

from pathlib import Path

from orbit.production.render_plan import RenderPlan


def _timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(plan: RenderPlan, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    cursor = 0.0
    for index, scene in enumerate(plan.scenes, start=1):
        start = cursor
        end = cursor + scene.duration_seconds
        lines.extend([
            str(index),
            f"{_timestamp(start)} --> {_timestamp(end)}",
            scene.narration.strip(),
            "",
        ])
        cursor = end
    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination
