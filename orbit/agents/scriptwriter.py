from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

from orbit.models import ResearchBrief, Script


class ScriptWriterAgent:
    """Write deterministic drafts or use a local Ollama model when enabled."""

    def __init__(self) -> None:
        self.provider = os.getenv("ORBIT_LLM_PROVIDER", "deterministic").lower()
        self.model = os.getenv("ORBIT_OLLAMA_MODEL", "")

    def _deterministic(self, brief: ResearchBrief, title: str | None = None) -> Script:
        final_title = title or f"What Nobody Is Seeing About {brief.topic}"
        hook = (
            f"Most people think they understand {brief.topic}. But the evidence points to a more interesting story. "
            "Here's what is happening, what we actually know, and what still does not add up."
        )
        body_parts = [
            f"Start with the core question: why does {brief.topic} matter now?",
            "The current evidence can be summarized from the research gathered for this episode.",
            brief.summary or "The research feed returned no usable material, so this draft must not be published.",
            "The important distinction is between what is verified, what is an interpretation, and what remains uncertain.",
        ]
        conclusion = (
            "The strongest takeaway is not the loudest claim. It is the part supported by evidence. "
            "ORBIT should replace this draft with a deeper, source-backed script before publishing."
        )
        return Script(
            title=final_title,
            hook=hook,
            body="\n\n".join(body_parts),
            conclusion=conclusion,
            claims=brief.claims,
        )

    def _ollama(self, brief: ResearchBrief, title: str | None = None) -> Script:
        if not self.model:
            raise RuntimeError("ORBIT_OLLAMA_MODEL must be set when ORBIT_LLM_PROVIDER=ollama")
        prompt = f"""
You are the lead documentary writer for ORBIT, a world-class but evidence-first YouTube channel.
Topic: {brief.topic}
Research brief:
{brief.summary}

Open questions:
{chr(10).join('- ' + q for q in brief.open_questions)}

Write an original 8-12 minute documentary draft. Do not invent facts. Keep uncertainty explicit.
Return EXACTLY these sections:
TITLE:
HOOK:
BODY:
CONCLUSION:

Make the hook specific and curiosity-driven. Use a strong narrative arc, not a listicle.
""".strip()
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=120) as response:
            data = json.loads(response.read())
        text = str(data.get("response", ""))
        sections: dict[str, str] = {}
        current = None
        for line in text.splitlines():
            upper = line.strip().upper()
            matched = next((name for name in ("TITLE", "HOOK", "BODY", "CONCLUSION") if upper.startswith(name + ":")), None)
            if matched:
                current = matched
                sections[current] = line.split(":", 1)[1].strip()
            elif current:
                sections[current] += ("\n" if sections[current] else "") + line.strip()
        if not all(sections.get(name) for name in ("TITLE", "HOOK", "BODY", "CONCLUSION")):
            raise ValueError("Local model output did not contain all required script sections")
        return Script(
            title=title or sections["TITLE"],
            hook=sections["HOOK"],
            body=sections["BODY"],
            conclusion=sections["CONCLUSION"],
            claims=brief.claims,
        )

    def write(self, brief: ResearchBrief, title: str | None = None) -> Script:
        if self.provider == "ollama":
            try:
                return self._ollama(brief, title=title)
            except Exception:
                # A local model is an enhancement, not a hard dependency for CI.
                return self._deterministic(brief, title=title)
        return self._deterministic(brief, title=title)
