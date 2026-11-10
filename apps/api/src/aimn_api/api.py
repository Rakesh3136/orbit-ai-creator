import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from aimn_api.db import get_db
from aimn_api.models import AgentTask, AgentEvaluation, Approval, Channel, Network, utc_now
from aimn_api.schemas import ApprovalDecision, ApprovalRead, ChannelCreate, ChannelRead, ChannelUpdate, NetworkCreate, NetworkRead, TaskCreate, TaskRead, EvaluationCreate, EvaluationRead, LessonDecision
from aimn_api.security import require_owner_or_api_key, require_owner_session
from aimn_api.agent_registry import REGISTRY_VERSION, get_agent, list_agent_records

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_owner_or_api_key)])

def channel_out(item: Channel) -> ChannelRead:
    return ChannelRead(
        id=item.id, network_id=item.network_id, name=item.name, slug=item.slug,
        description=item.description, niche=item.niche, primary_language=item.primary_language,
        target_regions=item.target_regions, status=item.status, youtube_channel_id=item.youtube_channel_id,
        connected=bool(item.youtube_channel_id and item.credential_ref), policy=item.policy,
        created_at=item.created_at, updated_at=item.updated_at,
    )

def get_active_network(db: Session, network_id: uuid.UUID) -> Network:
    network = db.get(Network, network_id)
    if network is None:
        raise HTTPException(status_code=404, detail="Network not found")
    if network.status != "active":
        raise HTTPException(status_code=409, detail="Network is not active")
    return network

@router.post("/networks", response_model=NetworkRead, status_code=201)
def create_network(payload: NetworkCreate, db: Session = Depends(get_db)):
    item = Network(name=payload.name.strip(), default_locale=payload.default_locale.lower())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/networks", response_model=list[NetworkRead])
def list_networks(db: Session = Depends(get_db)):
    return db.query(Network).order_by(Network.created_at.desc()).all()

@router.get("/networks/{network_id}", response_model=NetworkRead)
def get_network(network_id: uuid.UUID, db: Session = Depends(get_db)):
    item = db.get(Network, network_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Network not found")
    return item

@router.post("/networks/{network_id}/channels", response_model=ChannelRead, status_code=201)
def create_channel(network_id: uuid.UUID, payload: ChannelCreate, db: Session = Depends(get_db)):
    get_active_network(db, network_id)
    item = Channel(
        network_id=network_id, name=payload.name.strip(), slug=payload.slug,
        description=payload.description, niche=payload.niche,
        primary_language=payload.primary_language.lower(),
        target_regions=payload.target_regions, policy=payload.policy,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Channel slug or YouTube channel ID already exists")
    db.refresh(item)
    return channel_out(item)

@router.get("/networks/{network_id}/channels", response_model=list[ChannelRead])
def list_channels(
    network_id: uuid.UUID,
    channel_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    get_active_network(db, network_id)
    query = db.query(Channel).filter(Channel.network_id == network_id)
    if channel_status:
        if channel_status not in {"draft", "active", "paused", "archived"}:
            raise HTTPException(status_code=422, detail="Invalid channel status")
        query = query.filter(Channel.status == channel_status)
    return [channel_out(x) for x in query.order_by(Channel.created_at.desc()).offset(offset).limit(limit).all()]

@router.get("/networks/{network_id}/channels/{channel_id}", response_model=ChannelRead)
def get_channel(network_id: uuid.UUID, channel_id: uuid.UUID, db: Session = Depends(get_db)):
    get_active_network(db, network_id)
    item = db.query(Channel).filter(Channel.id == channel_id, Channel.network_id == network_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel_out(item)

@router.patch("/networks/{network_id}/channels/{channel_id}", response_model=ChannelRead)
def update_channel(network_id: uuid.UUID, channel_id: uuid.UUID, payload: ChannelUpdate, db: Session = Depends(get_db)):
    get_active_network(db, network_id)
    item = db.query(Channel).filter(Channel.id == channel_id, Channel.network_id == network_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No fields supplied")
    if any(v is None for k, v in changes.items() if k in {"status", "target_regions", "policy"}):
        raise HTTPException(status_code=422, detail="status, target_regions and policy cannot be null")
    if changes.get("name") is not None:
        changes["name"] = changes["name"].strip()
    if changes.get("primary_language") is not None:
        changes["primary_language"] = changes["primary_language"].lower()
    for key, value in changes.items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Channel update conflicts with an existing record")
    db.refresh(item)
    return channel_out(item)



def task_out(item: AgentTask) -> TaskRead:
    return TaskRead(
        id=item.id, network_id=item.network_id, channel_id=item.channel_id,
        parent_task_id=item.parent_task_id, agent_id=item.agent_id, title=item.title, instruction=item.instruction,
        status=item.status, external_action=item.external_action, result=item.result,
        error=item.error, created_at=item.created_at, updated_at=item.updated_at,
    )

def approval_out(item: Approval) -> ApprovalRead:
    return ApprovalRead(
        id=item.id, task_id=item.task_id, status=item.status,
        decision_note=item.decision_note, created_at=item.created_at,
        decided_at=item.decided_at,
    )

@router.get("/agents")
def list_agents():
    return list_agent_records()

@router.post("/networks/{network_id}/tasks", response_model=TaskRead, status_code=201)
def create_task(network_id: uuid.UUID, payload: TaskCreate, db: Session = Depends(get_db)):
    get_active_network(db, network_id)
    if get_agent(payload.agent_id) is None:
        raise HTTPException(status_code=422, detail="Unknown agent_id")
    if payload.channel_id:
        channel = db.query(Channel).filter(
            Channel.id == payload.channel_id, Channel.network_id == network_id
        ).first()
        if channel is None:
            raise HTTPException(status_code=404, detail="Channel not found in this network")
    item = AgentTask(
        network_id=network_id, channel_id=payload.channel_id,
        agent_id=payload.agent_id, title=payload.title.strip(),
        instruction=payload.instruction.strip(),
        input_payload=payload.input_payload,
        external_action=payload.external_action,
        status="awaiting_approval" if payload.external_action else "queued",
    )
    db.add(item)
    db.flush()
    if payload.external_action:
        db.add(Approval(task_id=item.id))
    db.commit()
    db.refresh(item)
    return task_out(item)

@router.get("/networks/{network_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    network_id: uuid.UUID,
    task_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    get_active_network(db, network_id)
    query = db.query(AgentTask).filter(AgentTask.network_id == network_id)
    if task_status:
        allowed = {"queued", "awaiting_approval", "running", "completed", "failed", "cancelled"}
        if task_status not in allowed:
            raise HTTPException(status_code=422, detail="Invalid task status")
        query = query.filter(AgentTask.status == task_status)
    return [task_out(x) for x in query.order_by(AgentTask.created_at.desc()).offset(offset).limit(limit).all()]

@router.get("/networks/{network_id}/approvals", response_model=list[ApprovalRead])
def list_approvals(
    network_id: uuid.UUID,
    approval_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    get_active_network(db, network_id)
    query = db.query(Approval).join(AgentTask).filter(AgentTask.network_id == network_id)
    if approval_status:
        if approval_status not in {"pending", "approved", "rejected"}:
            raise HTTPException(status_code=422, detail="Invalid approval status")
        query = query.filter(Approval.status == approval_status)
    return [approval_out(x) for x in query.order_by(Approval.created_at.desc()).limit(100).all()]

@router.post("/approvals/{approval_id}/decision", response_model=ApprovalRead)
def decide_approval(
    approval_id: uuid.UUID,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
):
    item = db.query(Approval).filter(Approval.id == approval_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    if item.status != "pending":
        raise HTTPException(status_code=409, detail="Approval has already been decided")
    task = db.get(AgentTask, item.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Associated task not found")
    from aimn_api.models import utc_now
    item.status = payload.decision
    item.decision_note = payload.note
    item.decided_at = utc_now()
    task.status = "queued" if payload.decision == "approved" else "cancelled"
    db.commit()
    db.refresh(item)
    return approval_out(item)

def evaluation_out(item: AgentEvaluation) -> EvaluationRead:
    return EvaluationRead(
        id=item.id, task_id=item.task_id, network_id=item.network_id,
        channel_id=item.channel_id, agent_id=item.agent_id, skill_id=item.skill_id,
        skill_version=item.skill_version, registry_version=item.registry_version,
        rating=item.rating, correction=item.correction, lesson=item.lesson,
        lesson_status=item.lesson_status, reviewer_email=item.reviewer_email,
        created_at=item.created_at, decided_at=item.decided_at, decision_note=item.decision_note,
    )


@router.get("/networks/{network_id}/evaluations", response_model=list[EvaluationRead])
def list_evaluations(network_id: uuid.UUID, db: Session = Depends(get_db)):
    get_active_network(db, network_id)
    rows = db.query(AgentEvaluation).filter(AgentEvaluation.network_id == network_id).order_by(AgentEvaluation.created_at.desc()).limit(100).all()
    return [evaluation_out(row) for row in rows]


@router.post("/networks/{network_id}/tasks/{task_id}/evaluation", response_model=EvaluationRead, status_code=201)
def create_evaluation(network_id: uuid.UUID, task_id: uuid.UUID, payload: EvaluationCreate, owner_email: str = Depends(require_owner_session), db: Session = Depends(get_db)):
    get_active_network(db, network_id)
    task = db.query(AgentTask).filter(AgentTask.id == task_id, AgentTask.network_id == network_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found in this network")
    if task.status != "completed" or task.external_action:
        raise HTTPException(status_code=409, detail="Only completed internal task outputs can be evaluated")
    if db.query(AgentEvaluation).filter(AgentEvaluation.task_id == task.id).first():
        raise HTTPException(status_code=409, detail="This task already has an evaluation")
    definition = get_agent(task.agent_id)
    if definition is None:
        raise HTTPException(status_code=409, detail="Task agent is no longer registered")
    result = task.result or {}
    item = AgentEvaluation(
        task_id=task.id, network_id=task.network_id, channel_id=task.channel_id,
        agent_id=task.agent_id, skill_id=definition.skill_id,
        skill_version=str(result.get("skill_version") or definition.skill_version),
        registry_version=str(result.get("registry_version") or REGISTRY_VERSION),
        rating=payload.rating, correction=payload.correction, lesson=payload.lesson,
        lesson_status="pending" if payload.lesson else "none",
        reviewer_email=owner_email.lower(),
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This task already has an evaluation")
    db.refresh(item)
    return evaluation_out(item)


@router.post("/evaluations/{evaluation_id}/lesson-decision", response_model=EvaluationRead)
def decide_lesson(evaluation_id: uuid.UUID, payload: LessonDecision, owner_email: str = Depends(require_owner_session), db: Session = Depends(get_db)):
    item = db.get(AgentEvaluation, evaluation_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    if not item.lesson or item.lesson_status != "pending":
        raise HTTPException(status_code=409, detail="No pending lesson requires a decision")
    item.lesson_status = payload.decision
    item.decision_note = payload.note
    item.decided_at = utc_now()
    db.commit()
    db.refresh(item)
    return evaluation_out(item)


@router.get("/networks/{network_id}/tasks/{task_id}/artifacts/{artifact}")
def get_task_artifact(
    network_id: uuid.UUID,
    task_id: uuid.UUID,
    artifact: str,
    db: Session = Depends(get_db),
):
    """Serve only known artifacts inside this task's production directory."""
    get_active_network(db, network_id)
    task = db.query(AgentTask).filter(
        AgentTask.id == task_id, AgentTask.network_id == network_id
    ).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    fields = {
        "video": "video_path",
        "captions": "captions_path",
        "provenance": "provenance_path",
        "package": "package_manifest_path",
    }
    field = fields.get(artifact)
    if field is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    raw_path = (task.result or {}).get(field)
    if not isinstance(raw_path, str) or not raw_path:
        raise HTTPException(status_code=404, detail="Artifact not available")
    root = Path(os.getenv("AIMN_PRODUCTION_ROOT", "data/production")).resolve()
    task_root = (root / str(network_id) / str(task_id)).resolve()
    path = Path(raw_path).resolve()
    try:
        path.relative_to(task_root)
    except ValueError:
        raise HTTPException(status_code=404, detail="Artifact not found")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Artifact not available")
    media_types = {
        "video": "video/mp4",
        "captions": "text/plain; charset=utf-8",
        "provenance": "application/json",
        "package": "application/json",
    }
    return FileResponse(path, media_type=media_types[artifact], filename=path.name)
