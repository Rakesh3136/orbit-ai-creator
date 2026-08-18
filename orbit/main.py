from orbit.agents.ideas import IdeaAgent
from orbit.agents.quality import QualityAgent
from orbit.memory import MemoryStore
from orbit.models import Idea, QualityReport


def main() -> None:
    memory = MemoryStore()
    ideas = [
        Idea(
            title="The AI Job Nobody Is Preparing For",
            premise="Explore an emerging role created by AI adoption and what skills it may require.",
            audience="curious adults interested in technology and careers",
            hook="Everyone talks about AI replacing jobs. Fewer people are asking what new jobs it creates.",
            differentiator="Focus on evidence and the underlying workflow rather than hype.",
            topic="AI and future of work",
            scores={
                "audience_demand": 17, "novelty": 12, "hook_strength": 14,
                "retention": 13, "story": 8, "search": 8, "monetization": 4,
                "feasibility": 5, "brand_fit": 5,
            },
        ),
        Idea(
            title="The Hidden System Behind Everyday AI",
            premise="Explain the invisible infrastructure that makes modern AI products possible.",
            audience="technology-curious viewers",
            hook="The AI you use every day depends on a massive system you almost never see.",
            differentiator="Tell the infrastructure story through one familiar product.",
            topic="technology infrastructure",
            scores={
                "audience_demand": 14, "novelty": 13, "hook_strength": 13,
                "retention": 12, "story": 9, "search": 7, "monetization": 4,
                "feasibility": 5, "brand_fit": 5,
            },
        ),
    ]

    ranked = IdeaAgent().rank(ideas)
    for idea in ranked:
        memory.remember("idea", f"{idea.title} | score={idea.score}")
        print(f"{idea.score:5.1f}  {idea.title}")

    report = QualityReport(80, 80, 80, 80, 80)
    print(f"Quality gate: {'PASS' if QualityAgent().approve(report) else 'BLOCK'} ({report.overall})")


if __name__ == "__main__":
    main()
