from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class CacheEntry(BaseModel):
    id: UUID
    project_id: UUID
    embedding: list[float]
    response: dict[str, Any]
    expires_at: datetime