import re
import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

ChannelStatus = Literal["draft", "active", "paused", "archived"]

class NetworkCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    default_locale: str = Field(default="en", min_length=2, max_length=20)

class NetworkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    default_locale: str
    status: Literal["active", "paused", "archived"]
    created_at: datetime
    updated_at: datetime

class ChannelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=1000)
    niche: str | None = Field(default=None, max_length=160)
    primary_language: str = Field(default="en", min_length=2, max_length=20)
    target_regions: list[str] = Field(default_factory=list, max_length=30)
    policy: dict = Field(default_factory=dict)

    @field_validator("slug")
    @classmethod
    def slug_format(cls, value: str):
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise ValueError("Use lowercase letters, numbers and single hyphens")
        return value

    @field_validator("target_regions")
    @classmethod
    def normalize_regions(cls, value):
        return [v.strip().upper() for v in value if v.strip()]

class ChannelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    niche: str | None = Field(default=None, max_length=160)
    primary_language: str | None = Field(default=None, min_length=2, max_length=20)
    target_regions: list[str] | None = Field(default=None, max_length=30)
    status: ChannelStatus | None = None
    policy: dict | None = None

class ChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    network_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    niche: str | None
    primary_language: str
    target_regions: list[str]
    status: ChannelStatus
    youtube_channel_id: str | None
    connected: bool
    policy: dict
    created_at: datetime
    updated_at: datetime
