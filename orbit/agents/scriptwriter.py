from __future__ import annotations

from orbit.models import ResearchBrief, Script


class ScriptWriterAgent:
    """Deterministic local script draft.

    This is intentionally provider-free. A local/open model can later replace
    the drafting function without changing the pipeline contract.
    """

    def write(self, brief: ResearchBrief, title: str | None = None) -> Script:
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
