"""AIMN local task runtime with bounded CEO orchestration and local production.

Specialists use deterministic local handlers. Producer tasks may render an
owner-supplied script through ORBIT and write only to the local data directory.
No LLM, live research, YouTube access, comments, uploads, or external actions
are executed.
"""
from __future__ import annotations
import os
from pathlib import Path
from collections.abc import Callable
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from aimn_api.models import AgentTask, AgentEvaluation
from aimn_api.agent_registry import REGISTRY_VERSION, get_agent
from orbit.models import ResearchBrief, Script
from orbit.agents.scriptwriter import ScriptWriterAgent
from orbit.production.episode import EpisodeRenderer
from orbit.production.package import PublishingPackage
from orbit.production.render_plan import build_render_plan

def _brief(task: AgentTask, kind: str, steps: list[str], caution: str) -> dict[str, Any]:
    definition = get_agent(task.agent_id)
    if definition is None:
        raise ValueError(f"No agent definition registered for '{task.agent_id}'")
    return {
        "mode": definition.execution_mode,
        "agent_id": task.agent_id,
        "registry_version": REGISTRY_VERSION,
        "skill_id": definition.skill_id,
        "skill_version": definition.skill_version,
        "allowed_tools": list(definition.allowed_tools),
        "external_writes": definition.external_writes,
        "max_paid_provider_cost_usd": definition.max_paid_provider_cost_usd,
        "paid_provider_used": False,
        "deliverable": kind,
        "task": task.title,
        "brief": task.instruction,
        "approved_lessons_context": (task.result or {}).get("approved_lessons_context", []),
        "steps": steps,
        "cautions": [caution],
        "provider_connected": False,
    }

def research(t):
    return _brief(t,"research_brief",["Break the request into research questions.","Identify primary and authoritative sources to consult.","Record each claim with source URL, date and confidence.","Separate verified facts from assumptions and open questions.","Prepare an evidence-backed summary."],"No live web search was performed.")

def strategist(t):
    return _brief(t,"channel_strategy_brief",["Define the target audience and viewer problem.","Write a positioning statement and differentiator.","Propose three repeatable content pillars.","Define a small test batch and measurable success criteria.","Review results before scaling."],"Audience demand remains a hypothesis until validated with research and analytics.")

def writer(t):
    result = _brief(
        t, "script_development_brief",
        ["Turn the creator objective into a structured first-draft script.",
         "Keep unsupported claims explicitly provisional.",
         "Prepare title, hook, body and conclusion for the Producer handoff.",
         "Require editorial and source review before publication."],
        "This is a deterministic local draft. No verified research sources were supplied.",
    )
    payload = t.input_payload if isinstance(t.input_payload, dict) else {}
    topic = str(payload.get("topic") or t.instruction or t.title).strip()[:180]
    research_summary = str(payload.get("research_summary") or
        "No verified research evidence was attached to this task. Treat all factual statements as provisional.")
    brief = ResearchBrief(
        topic=topic or t.title,
        summary=research_summary,
        open_questions=[
            "Which primary sources verify the key claims?",
            "What recent evidence could change the conclusion?",
            "Which statements are interpretation rather than established fact?",
        ],
    )
    script = ScriptWriterAgent().write(brief)
    result.update({
        "script": {"title": script.title, "hook": script.hook,
                   "body": script.body, "conclusion": script.conclusion},
        "script_status": "draft_unverified",
        "source_count": len(script.claims),
        "editorial_review_required": True,
        "production_handoff_ready": True,
    })
    return result

def fact_checker(t):
    return _brief(t,"fact_check_brief",["Extract factual, numerical and time-sensitive claims.","Find primary evidence for material claims.","Check dates, context, units and wording.","Flag unsupported or disputed statements.","Return corrections with evidence."],"No external sources were checked.")

def producer(t, generated_script: dict[str, Any] | None = None):
    payload = t.input_payload or {}
    script_data = payload.get("script") if isinstance(payload, dict) else None
    script_origin = "owner_supplied" if script_data else "writer_agent_draft"
    if not script_data:
        script_data = generated_script
    if not script_data:
        return _brief(t,"production_brief",["Convert the approved script into scenes.","Specify narration, on-screen text and visual assets.","Flag rights-sensitive assets.","Prepare edit sequence and quality checklist.","Confirm audio, captions and export settings."],"No script payload was supplied; no media files were generated.")
    required = ("title", "hook", "body", "conclusion")
    if not isinstance(script_data, dict) or any(not isinstance(script_data.get(key), str) or not script_data[key].strip() for key in required):
        raise ValueError("Producer input_payload.script must contain non-empty title, hook, body and conclusion strings")
    if any(len(script_data[key]) > limit for key, limit in (("title",180),("hook",2000),("body",12000),("conclusion",2000))):
        raise ValueError("Production script exceeds a field length limit")
    script = Script(title=script_data["title"].strip(), hook=script_data["hook"].strip(),
                    body=script_data["body"].strip(), conclusion=script_data["conclusion"].strip())
    plan = build_render_plan(script)
    if len(plan.scenes) > 12 or sum(scene.duration_seconds for scene in plan.scenes) > 240:
        raise ValueError("Production render is limited to 12 scenes and 4 minutes")
    backend = payload.get("narration_backend", "auto")
    if backend not in {"auto", "espeak", "silent"}:
        raise ValueError("narration_backend must be auto, espeak or silent")
    output = Path(os.getenv("AIMN_PRODUCTION_ROOT", "data/production")) / str(t.network_id) / str(t.id)
    output.mkdir(parents=True, exist_ok=True)
    video = output / "episode.mp4"
    rendered = EpisodeRenderer().render(plan, video, narration_backend=backend)
    manifest = PublishingPackage([], "", [], [], "", "").write(
        output / "package", script, video_path=str(rendered.video_path),
        captions_path=str(rendered.captions_path), provenance_path=str(rendered.provenance_path))
    result = _brief(t,"production_render",["Render scene cards and local narration with FFmpeg.","Generate an SRT subtitle file.","Record generated asset hashes and provenance.","Prepare a private-by-default publishing package."],"Local rendering only. No assets were downloaded and nothing was uploaded or published.")
    result.update({
        "mode":"orbit_local_production",
        "render_status":"completed",
        "video_path":str(rendered.video_path),
        "captions_path":str(rendered.captions_path),
        "provenance_path":str(rendered.provenance_path),
        "package_manifest_path":str(manifest),
        "narration_backend":rendered.narration_backend,
        "script_origin":script_origin,
        "script_status":"draft_unverified" if script_origin == "writer_agent_draft" else "owner_supplied_pending_review",
        "editorial_review_required":True,
        "scene_count":len(plan.scenes),
        "duration_seconds":sum(scene.duration_seconds for scene in plan.scenes),
        "external_writes":False,
        "paid_provider_used":False,
    })
    return result

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
CEO_STEPS = (
    ("research","Research brief"),
    ("strategist","Channel strategy"),
    ("writer","Script development"),
    ("fact-checker","Editorial fact-check"),
    ("producer","Production plan"),
)
MAX_CEO_CHILDREN = 5

def _orchestrate(db: Session, task: AgentTask) -> None:
    """Create a fixed, bounded specialist workflow; never dispatch external actions."""
    definition = get_agent(task.agent_id)
    if definition is None:
        raise ValueError(f"No agent definition registered for '{task.agent_id}'")
    children = []
    supplied_payload = task.input_payload if isinstance(task.input_payload, dict) else {}
    for agent_id, label in CEO_STEPS[:MAX_CEO_CHILDREN]:
        # Forward owner-supplied render inputs only to the Producer.
        producer_payload = {}
        if agent_id == "producer":
            for key in ("script", "narration_backend"):
                if key in supplied_payload:
                    producer_payload[key] = supplied_payload[key]
        child = AgentTask(
            network_id=task.network_id, channel_id=task.channel_id,
            parent_task_id=task.id, agent_id=agent_id,
            title=f"{label}: {task.title}"[:180],
            instruction=f"Objective: {task.instruction}\nYour role: {label}. Return a useful, specific planning artifact.",
            input_payload=producer_payload,
            status="queued", external_action=False,
        )
        db.add(child)
        children.append(child)
    db.flush()
    task.result = {
        "mode":"local_ceo_orchestration",
        "registry_version":REGISTRY_VERSION,
        "skill_id":definition.skill_id,
        "skill_version":definition.skill_version,
        "agent_versions":[{"agent_id":agent_id,"skill_id":get_agent(agent_id).skill_id,"skill_version":get_agent(agent_id).skill_version} for agent_id, _ in CEO_STEPS[:MAX_CEO_CHILDREN]],
        "external_writes":False,
        "max_paid_provider_cost_usd":0.0,
        "paid_provider_used":False,
        "provider_connected":False,
        "workflow":"research_strategy_editorial_production",
        "child_task_ids":[str(child.id) for child in children],
        "planned_agents":[agent_id for agent_id, _ in CEO_STEPS[:MAX_CEO_CHILDREN]],
        "max_children":MAX_CEO_CHILDREN,
        "cautions":["Deterministic workflow; no LLM or live research provider is connected.",
                    "All child tasks are internal planning tasks; publishing remains disabled."],
    }
    task.status = "running"
    db.commit()

def _finalize_ready_orchestrations(db: Session) -> bool:
    parents = db.execute(select(AgentTask).where(
        AgentTask.agent_id=="ceo", AgentTask.status=="running"
    )).scalars().all()
    changed = False
    for parent in parents:
        if parent.result.get("mode") != "local_ceo_orchestration":
            continue
        children = db.execute(select(AgentTask).where(
            AgentTask.parent_task_id==parent.id
        ).order_by(AgentTask.created_at.asc(), AgentTask.id.asc())).scalars().all()
        if not children or any(child.status in {"queued","running","awaiting_approval"} for child in children):
            continue
        parent.result = {
            **parent.result,
            "status":"failed" if any(child.status != "completed" for child in children) else "completed",
            "specialist_results":[
                {"agent_id":child.agent_id,"task_id":str(child.id),"status":child.status,
                 "result":child.result if child.status=="completed" else None,
                 "error":child.error}
                for child in children
            ],
            "summary":"All specialist planning steps completed." if all(c.status=="completed" for c in children)
                     else "One or more specialist steps failed; review the errors before proceeding.",
        }
        parent.status = "failed" if any(child.status != "completed" for child in children) else "completed"
        if parent.status == "failed":
            parent.error = "One or more CEO specialist tasks failed"
        db.add(parent)
        changed = True
    if changed:
        db.commit()
    return changed

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
        _finalize_ready_orchestrations(db)
        task=claim_next(db)
        if task is None:
            _finalize_ready_orchestrations(db)
            return "idle"
        task_id=task.id
        try:
            if task.agent_id == "ceo":
                _orchestrate(db, task)
                return "orchestrating"
            handler=HANDLERS.get(task.agent_id)
            if handler is None: raise ValueError(f"No local handler registered for agent '{task.agent_id}'")
            generated_script = None
            if task.agent_id == "producer" and task.parent_task_id and not (task.input_payload or {}).get("script"):
                writer_task = db.execute(select(AgentTask).where(
                    AgentTask.parent_task_id == task.parent_task_id,
                    AgentTask.agent_id == "writer",
                    AgentTask.status == "completed",
                ).order_by(AgentTask.created_at.asc()).limit(1)).scalars().first()
                if writer_task is not None:
                    generated_script = (writer_task.result or {}).get("script")
            lessons = db.execute(select(AgentEvaluation).where(
                AgentEvaluation.network_id == task.network_id,
                AgentEvaluation.lesson_status == "approved",
                AgentEvaluation.lesson.is_not(None),
                AgentEvaluation.channel_id.is_(None) if task.channel_id is None else
                    ((AgentEvaluation.channel_id.is_(None)) | (AgentEvaluation.channel_id == task.channel_id)),
            ).order_by(AgentEvaluation.decided_at.desc(), AgentEvaluation.created_at.desc()).limit(8)).scalars().all()
            task.result = {"approved_lessons_context": [
                {"evaluation_id": str(x.id), "lesson": x.lesson, "agent_id": x.agent_id,
                 "skill_id": x.skill_id, "skill_version": x.skill_version,
                 "rating": x.rating, "scope": "network" if x.channel_id is None else "channel"}
                for x in lessons
            ]}
            if task.agent_id == "producer":
                task.result.update(producer(task, generated_script=generated_script))
            else:
                task.result.update(handler(task))
            task.status="completed"; task.error=None
            db.commit()
            _finalize_ready_orchestrations(db)
            return "completed"
        except Exception as exc:
            db.rollback()
            failed=db.get(AgentTask,task_id)
            if failed is not None:
                failed.status="failed"; failed.error=str(exc)[:2000]; db.commit()
            return "failed"
