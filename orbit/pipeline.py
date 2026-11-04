from __future__ import annotations

from dataclasses import dataclass
import os

from orbit.agents.ideas import IdeaAgent
from orbit.agents.research import ResearchAgent
from orbit.agents.scriptwriter import ScriptWriterAgent
from orbit.agents.quality import QualityAgent
from orbit.learning.feedback import LearningMemory, TaskEvaluation
from orbit.memory import MemoryStore
from orbit.models import Idea, QualityReport, ResearchBrief, Script


@dataclass(frozen=True)
class PipelineResult:
    topic: str
    brief: ResearchBrief
    script: Script
    quality: QualityReport
    lessons_considered: tuple[str, ...] = ()
    evaluation_id: int | None = None


class CreatorPipeline:
    def __init__(
        self,
        memory: MemoryStore | None = None,
        learning_memory: LearningMemory | None = None,
        network_id: str | None = None,
        channel_id: str | None = None,
    ) -> None:
        self.memory = memory or MemoryStore()
        self.learning_memory = learning_memory or LearningMemory()
        self.network_id = network_id or os.getenv("ORBIT_NETWORK_ID", "default")
        self.channel_id = channel_id if channel_id is not None else os.getenv("ORBIT_CHANNEL_ID", "")
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
        # Only explicitly recorded human feedback is returned as a lesson.
        lessons = tuple(self.learning_memory.lessons("scriptwriter", "script", network_id=self.network_id, channel_id=self.channel_id))
        results = self.research.search(topic, limit=8)
        brief = self.research.build_brief(topic, results)
        script = self.writer.write(brief, title=title, lessons=list(lessons))
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

        # This is an unapproved evaluation: it records quality signals but never
        # grants permission to publish or marks the work as human-approved.
        evaluation_id = self.learning_memory.record(
            TaskEvaluation(
                agent="scriptwriter",
                task_type="script",
                scores={
                    "content": content,
                    "originality": originality,
                    "factuality": factuality,
                    "retention": retention,
                    "compliance": compliance,
                },
                feedback="",
                approved=False,
            ),
            network_id=self.network_id,
            channel_id=self.channel_id,
            provenance="creator-pipeline:heuristic-quality-v1",
        )
        return PipelineResult(
            topic=topic,
            brief=brief,
            script=script,
            quality=report,
            lessons_considered=lessons,
            evaluation_id=evaluation_id,
        )
