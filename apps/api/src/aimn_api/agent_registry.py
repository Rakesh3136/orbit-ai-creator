"""Versioned, zero-paid-provider agent catalogue for AIMN.

This registry describes the capabilities that are actually enabled today.
Agents run deterministic local planning handlers only; tool access and
external writes remain denied until separately implemented and approved.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

REGISTRY_VERSION = "1.0.0"


@dataclass(frozen=True)
class AgentDefinition:
    id: str
    name: str
    department: str
    description: str
    skill_id: str
    skill_version: str
    execution_mode: str = "local_planning_only"
    allowed_tools: tuple[str, ...] = ()
    external_writes: bool = False
    max_paid_provider_cost_usd: float = 0.0


AGENT_DEFINITIONS: tuple[AgentDefinition, ...] = (
    AgentDefinition(
        "ceo", "AI CEO / Orchestrator", "Executive",
        "Breaks a creator objective into a bounded specialist workflow and combines the results.",
        "executive.workflow_orchestration", "1.0.0",
    ),
    AgentDefinition(
        "research", "Research & Intelligence", "Research",
        "Builds research questions, source plans and evidence-backed briefs.",
        "research.topic_discovery", "1.0.0",
    ),
    AgentDefinition(
        "strategist", "Channel Strategist", "Strategy",
        "Turns channel goals into positioning, content pillars and measurable experiments.",
        "strategy.channel_positioning", "1.0.0",
    ),
    AgentDefinition(
        "writer", "Editorial & Scriptwriter", "Editorial",
        "Plans original scripts, hooks, titles and descriptions.",
        "editorial.script_development", "1.0.0",
    ),
    AgentDefinition(
        "fact-checker", "Fact Checker", "Quality",
        "Identifies factual claims, evidence gaps and uncertainty.",
        "quality.claim_verification", "1.0.0",
    ),
    AgentDefinition(
        "producer", "Creative Producer", "Production",
        "Prepares scene, narration, visual and edit specifications.",
        "production.preproduction", "1.0.0",
    ),
    AgentDefinition(
        "growth-analyst", "Growth Analyst", "Growth",
        "Defines channel metrics and testable growth hypotheses.",
        "growth.performance_analysis", "1.0.0",
    ),
    AgentDefinition(
        "community", "Community Manager", "Community",
        "Classifies comments and drafts replies for owner review.",
        "community.comment_triage", "1.0.0",
    ),
    AgentDefinition(
        "publisher", "Publishing Manager", "Publishing",
        "Prepares metadata and publishing checklists without publishing.",
        "publishing.metadata_preparation", "1.0.0",
    ),
)

_BY_ID = {agent.id: agent for agent in AGENT_DEFINITIONS}


def get_agent(agent_id: str) -> AgentDefinition | None:
    return _BY_ID.get(agent_id)


def list_agent_records() -> list[dict]:
    """Return JSON-ready copies; callers cannot mutate the registry."""
    records = []
    for agent in AGENT_DEFINITIONS:
        record = asdict(agent)
        record["registry_version"] = REGISTRY_VERSION
        record["allowed_tools"] = list(agent.allowed_tools)
        records.append(record)
    return records
