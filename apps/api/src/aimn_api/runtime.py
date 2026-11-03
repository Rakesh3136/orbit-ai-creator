"""AIMN local task runtime.

This executor creates deterministic planning briefs only. It does not claim to
perform live research, call an LLM, access YouTube, or publish external content.
"""
from __future__ import annotations
from collections.abc import Callable
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from aimn_api.models import AgentTask

def _brief(task: AgentTask, kind: str, steps: list[str], caution: str) -> dict[str, Any]:
    return {"mode":"local_planning_only","agent_id":task.agent_id,"deliverable":kind,
            "task":task.title,"brief":task.instruction,"steps":steps,
            "cautions":[caution],"provider_connected":False}

def research(t):
    return _brief(t,"research_brief",["Break the request into research questions.","Identify primary and authoritative sources to consult.","Record each claim with source URL, date and confidence.","Separate verified facts from assumptions and open questions.","Prepare an evidence-backed summary."],"No live web search was performed.")

def strategist(t):
    return _brief(t,"channel_strategy_brief",["Define the target audience and viewer problem.","Write a positioning statement and differentiator.","Propose three repeatable content pillars.","Define a small test batch and measurable success criteria.","Review results before scaling."],"Audience demand remains a hypothesis until validated with research and analytics.")

def writer(t):
    return _brief(t,"script_development_brief",["Define one audience promise and opening hook.","Build a clear beginning, middle and ending.","Attach source notes to factual claims.","Plan visual changes that improve clarity.","Finish with a relevant, non-misleading viewer action."],"This is a drafting brief, not a completed script.")

def fact_checker(t):
    return _brief(t,"fact_check_brief",["Extract factual, numerical and time-sensitive claims.","Find primary evidence for material claims.","Check dates, context, units and wording.","Flag unsupported or disputed statements.","Return corrections with evidence."],"No external sources were checked.")

def producer(t):
    return _brief(t,"production_brief",["Convert the approved script into scenes.","Specify narration, on-screen text and visual assets.","Flag rights-sensitive assets.","Prepare edit sequence and quality checklist.","Confirm audio, captions and export settings."],"No media files were generated or downloaded.")

def growth(t):
    return _brief(t,"growth_analysis_brief",["Define the channel objective and success metric.","Collect impressions, CTR, watch time and retention.","Compare performance by topic and format.","Form one testable hypothesis.","Set a review window and record results."],"No YouTube Analytics data was accessed.")

def community(t):
    return _brief(t,"community_response_brief",["Classify comments by question, feedback, spam or safety issue.","Draft concise, respectful replies using confirmed facts.","Escalate personal data, threats and sensitive issues.","Require owner review before sending."],"No comments were accessed and no replies were sent.")

def publisher(t):
    return _brief(t,"publishing_checklist",["Confirm video and thumbnail owner approval.","Validate title, description, audience and captions.","Check rights and platform policy requirements.","Prepare a metadata preview.","Require explicit approval immediately before any external publish call."],"Publishing is disabled; no upload or external action was attempted.")

HANDLERS: dict[str, Callable[[AgentTask], dict[str, Any]]] = {
    "research":research,"strategist":strategist,"writer":writer,"fact-checker":fact_checker,
    "producer":producer,"growth-analyst":growth,"community":community,"publisher":publisher,
}

def claim_next(db: Session) -> AgentTask | None:
    stmt=(select(AgentTask).where(AgentTask.status=="queued",AgentTask.external_action.is_(False))
          .order_by(AgentTask.created_at.asc(),AgentTask.id.asc()).limit(1).with_for_update(skip_locked=True))
    task=db.execute(stmt).scalars().first()
    if task is None: return None
    task.status="running"; task.error=None
    db.commit(); db.refresh(task)
    return task

def run_once(session_factory: sessionmaker) -> str:
    with session_factory() as db:
        task=claim_next(db)
        if task is None: return "idle"
        task_id=task.id
        try:
            handler=HANDLERS.get(task.agent_id)
            if handler is None: raise ValueError(f"No local handler registered for agent '{task.agent_id}'")
            task.result=handler(task); task.status="completed"; task.error=None
            db.commit()
            return "completed"
        except Exception as exc:
            db.rollback()
            failed=db.get(AgentTask,task_id)
            if failed is not None:
                failed.status="failed"; failed.error=str(exc)[:2000]; db.commit()
            return "failed"
