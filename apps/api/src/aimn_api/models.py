import uuid
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def utc_now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class Network(Base):
    __tablename__ = "networks"
    __table_args__ = (CheckConstraint("status IN ('active','paused','archived')", name="ck_networks_status"),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    default_locale: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, server_default=func.now())
    channels: Mapped[list["Channel"]] = relationship(back_populates="network", cascade="all, delete-orphan")
    tasks: Mapped[list["AgentTask"]] = relationship(back_populates="network", cascade="all, delete-orphan")

class Channel(Base):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("network_id", "slug", name="uq_channels_network_slug"),
        UniqueConstraint("youtube_channel_id", name="uq_channels_youtube_channel_id"),
        CheckConstraint("status IN ('draft','active','paused','archived')", name="ck_channels_status"),
        Index("ix_channels_network_id", "network_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("networks.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    niche: Mapped[str | None] = mapped_column(String(160))
    primary_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    target_regions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    youtube_channel_id: Mapped[str | None] = mapped_column(String(128))
    credential_ref: Mapped[str | None] = mapped_column(String(255))
    policy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, server_default=func.now())
    network: Mapped[Network] = relationship(back_populates="channels")

class AgentTask(Base):
    __tablename__ = "agent_tasks"
    __table_args__ = (
        CheckConstraint("status IN ('queued','awaiting_approval','running','completed','failed','cancelled')", name="ck_agent_tasks_status"),
        Index("ix_agent_tasks_network_created", "network_id", "created_at"),
        Index("ix_agent_tasks_parent", "parent_task_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    network_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("networks.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("channels.id", ondelete="SET NULL"))
    parent_task_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agent_tasks.id", ondelete="CASCADE"))
    agent_id: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False)
    external_action: Mapped[bool] = mapped_column(default=False, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, server_default=func.now())
    network: Mapped[Network] = relationship(back_populates="tasks")
    parent: Mapped["AgentTask | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["AgentTask"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="task", cascade="all, delete-orphan")

class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (CheckConstraint("status IN ('pending','approved','rejected')", name="ck_approvals_status"),)
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("agent_tasks.id", ondelete="CASCADE"), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    decision_note: Mapped[str | None] = mapped_column(String(1000))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    task: Mapped[AgentTask] = relationship(back_populates="approvals")

class AgentEvaluation(Base):
    __tablename__ = "agent_evaluations"
    __table_args__ = (
        UniqueConstraint("task_id", name="uq_agent_evaluations_task_id"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_agent_evaluations_rating"),
        CheckConstraint("lesson_status IN ('none','pending','approved','rejected')", name="ck_agent_evaluations_lesson_status"),
        Index("ix_agent_evaluations_scope_status", "network_id", "channel_id", "lesson_status"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("agent_tasks.id", ondelete="CASCADE"), nullable=False)
    network_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("networks.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"))
    agent_id: Mapped[str] = mapped_column(String(80), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(160), nullable=False)
    skill_version: Mapped[str] = mapped_column(String(40), nullable=False)
    registry_version: Mapped[str] = mapped_column(String(40), nullable=False)
    rating: Mapped[int] = mapped_column(nullable=False)
    correction: Mapped[str | None] = mapped_column(Text)
    lesson: Mapped[str | None] = mapped_column(Text)
    lesson_status: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    reviewer_email: Mapped[str] = mapped_column(String(254), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, server_default=func.now())
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_note: Mapped[str | None] = mapped_column(String(1000))
