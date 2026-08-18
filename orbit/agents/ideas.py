from __future__ import annotations

from orbit.models import Idea


class IdeaAgent:
    """Generate and rank ideas. Provider/model calls will be added in the next phase."""

    WEIGHTS = {
        "audience_demand": 20,
        "novelty": 15,
        "hook_strength": 15,
        "retention": 15,
        "story": 10,
        "search": 10,
        "monetization": 5,
        "feasibility": 5,
        "brand_fit": 5,
    }

    def score(self, idea: Idea) -> float:
        return idea.score

    def rank(self, ideas: list[Idea], minimum: float = 70) -> list[Idea]:
        return sorted((i for i in ideas if i.score >= minimum), key=self.score, reverse=True)
