import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from aimn_api.db import get_db
from aimn_api.models import Channel, Network
from aimn_api.schemas import ChannelCreate, ChannelRead, ChannelUpdate, NetworkCreate, NetworkRead
from aimn_api.security import require_admin_api_key

router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_admin_api_key)])

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
