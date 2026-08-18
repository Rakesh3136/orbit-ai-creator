from __future__ import annotations

from dataclasses import dataclass

from orbit.agents.ideas import IdeaAgent
from orbit.agents.research import ResearchAgent
from orbit.agents.scriptwriter import ScriptWriterAgent
from orbit.agents.quality import QualityAgent
from orbit.memory import MemoryStore
from orbit.models import Idea, QualityReport, ResearchBrief, Script


@dataclass(frozen=True)
class PipelineResult:
    topic: str
    brief: ResearchBrief
    script: Script
    quality: QualityReport


class CreatorPipeline:
    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or MemoryStore()
        self.research = ResearchAgent()
        self.ideas = IdeaAgent()
        self.writer = ScriptWriterAgent()
        self.quality_agent = QualityAgent()

    def discover(self, topics: list[str]) -> list[Idea]:
        ideas: list[Idea] = []
        for topic in topics:
            results = self.research.search(topic, limit=5)
            evidence_bonus = min(len(results), 5)
            ideas.append(
                Idea(
                    title=f"The Story Behind {topic.title()}",
                    premise=f"Investigate what is changing around {topic} and why it matters.",
                    audience="curious adults interested in technology, science, business and the future",
                    hook=f"Something important is changing around {topic}, but the obvious explanation may be incomplete.",
                    differentiator="Evidence-first investigation rather than listicle commentary.",
                    topic=topic,
                    scores={
                        "audience_demand": 12 + evidence_bonus,
                        "novelty": 10,
                        "hook_strength": 12,
                        "retention": 11,
                        "story": 8,
                        "search": 8,
                        "monetization": 3,
                        "feasibility": 5,
                        "brand_fit": 5,
                    },
                )
            )
        return self.ideas.rank(ideas, minimum=60)

    def run(self, topic: str, title: str | None = None) -> PipelineResult:
        results = self.research.search(topic, limit=8)
        brief = self.research.build_brief(topic, results)
        script = self.writer.write(brief, title=title)
        self.memory.remember("research", brief.summary)
        self.memory.remember("script", script.title)

        factuality = 85.0 if results else 20.0
        originality = 80.0
        content = 80.0 if brief.summary else 20.0
        retention = 70.0 if script.hook else 0.0
        compliance = 90.0
        report = QualityReport(content, originality, factuality, retention, compliance)
        if not results:
            report.notes.append("No research results. Publishing is blocked.")
        if any(c.confidence == "low" for c in brief.claims):
            report.notes.append("Research claims are provisional; primary-source verification is required.")
        return PipelineResult(topic=topic, brief=brief, script=script, quality=report)
