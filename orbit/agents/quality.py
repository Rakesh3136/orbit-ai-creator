from orbit.models import QualityReport


class QualityAgent:
    """Hard quality gate used before any future publishing action."""

    def __init__(self, minimum_overall: float = 75.0):
        self.minimum_overall = minimum_overall

    def approve(self, report: QualityReport) -> bool:
        return report.overall >= self.minimum_overall and not any(
            note.startswith("BLOCK:") for note in report.notes
        )
