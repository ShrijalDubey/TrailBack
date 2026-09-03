from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class APIKey(BaseModel):
    id: UUID
    project_id: UUID
    key_hash: str
    prefix: str
    revoked_at: datetime | None = None