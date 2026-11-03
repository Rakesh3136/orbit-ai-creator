import uuid
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, JSON, String, UniqueConstraint, Uuid, func
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
