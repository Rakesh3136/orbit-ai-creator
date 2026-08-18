from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    publisher: str = ""
    reliability: float = 0.0


@dataclass
class Idea:
    title: str
    premise: str
    audience: str
    hook: str
    differentiator: str
    topic: str
    scores: dict[str, float] = field(default_factory=dict)

    @property
    def score(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(self.scores.values()), 1)


@dataclass
class Claim:
    text: str
    sources: list[Source] = field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "low"


@dataclass
class ResearchBrief:
    topic: str
    summary: str
    claims: list[Claim] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)


@dataclass
class Script:
    title: str
    hook: str
    body: str
    conclusion: str
    claims: list[Claim] = field(default_factory=list)


@dataclass
class QualityReport:
    content: float
    originality: float
    factuality: float
    retention: float
    compliance: float
    notes: list[str] = field(default_factory=list)

    @property
    def overall(self) -> float:
        return round((self.content + self.originality + self.factuality + self.retention + self.compliance) / 5, 1)
