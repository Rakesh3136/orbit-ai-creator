from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from orbit.models import Script
from orbit.production.render_plan import build_render_plan


@dataclass(frozen=True)
class PublishingPackage:
    title_options: list[str]
    description: str
    tags: list[str]
    chapters: list[str]
    script_path: str
    render_plan_path: str
    video_path: str = ""
    captions_path: str = ""
    provenance_path: str = ""
    upload_privacy: str = "private"
    human_approval_required: bool = True

    def write(
        self,
        directory: str | Path,
        script: Script,
        *,
        video_path: str = "",
        captions_path: str = "",
        provenance_path: str = "",
    ) -> Path:
        destination = Path(directory)
        destination.mkdir(parents=True, exist_ok=True)
        script_path = destination / "script.txt"
        script_path.write_text(
            f"{script.hook}\n\n{script.body}\n\n{script.conclusion}\n",
            encoding="utf-8",
        )
        plan = build_render_plan(script)
        plan_path = plan.write_json(destination / "render_plan.json")
        package = PublishingPackage(
            title_options=[script.title, f"The Story Behind {script.title}"],
            description=(
                f"ORBIT documentary: {script.title}.\n\n"
                "This episode is based on research and is subject to final human editorial review."
            ),
            tags=["ORBIT", "documentary", "technology", "science", "business", "future"],
            chapters=[],
            script_path=str(script_path),
            render_plan_path=str(plan_path),
            video_path=video_path,
            captions_path=captions_path,
            provenance_path=provenance_path,
        )
        manifest = destination / "publishing_package.json"
        manifest.write_text(json.dumps(asdict(package), indent=2, ensure_ascii=False), encoding="utf-8")
        return manifest
