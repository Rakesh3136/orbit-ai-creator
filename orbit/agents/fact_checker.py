from orbit.models import Claim, ResearchBrief


class FactChecker:
    """Conservative fact-check gate; real source retrieval is plugged in later."""

    def check(self, brief: ResearchBrief) -> list[str]:
        problems: list[str] = []
        for claim in brief.claims:
            if not claim.sources:
                problems.append(f"BLOCK: unsupported claim: {claim.text}")
            elif claim.confidence == "low":
                problems.append(f"BLOCK: low-confidence claim: {claim.text}")
        return problems
