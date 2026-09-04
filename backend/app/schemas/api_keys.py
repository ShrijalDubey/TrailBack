from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIKeyCreate(BaseModel):
    project_id: UUID


class APIKeyCreated(BaseModel):

    id: UUID
    project_id: UUID
    prefix: str
    api_key: str
    created_at: datetime


class APIKey(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    prefix: str
    revoked_at: datetime | None = None
    created_at: datetime