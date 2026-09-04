from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    user_id: UUID
    name: str = Field(min_length=1, max_length=255)
    policy_id: UUID | None = None
    retention: int = Field(ge=0, default=0)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    policy_id: UUID | None = None
    retention: int | None = Field(default=None, ge=0)


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str = Field(min_length=1, max_length=255)
    policy_id: UUID | None = None
    retention: int = Field(ge=0)


class Budget(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    period: str

    limit: float = Field(ge=0)
    current_spend: float = Field(ge=0)


class Alert(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    type: str
    threshold: float = Field(ge=0)
    status: str
    triggered_at: datetime | None = None