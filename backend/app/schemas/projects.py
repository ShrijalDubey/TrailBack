from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class Project(BaseModel):
    id: UUID
    user_id: UUID
    name: str = Field(min_length=1, max_length=255)
    policy_id: UUID | None = None
    retention: int = Field(ge=0)

class Budget(BaseModel):
    project_id: UUID
    period: str

    limit: float = Field(ge=0)
    current_spend: float = Field(ge=0)

class Alert(BaseModel):
    project_id: UUID
    type: str
    threshold: float = Field(ge=0)
    status: str
    triggered_at: datetime | None = None