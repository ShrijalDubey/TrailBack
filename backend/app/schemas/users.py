from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: UUID
    email: EmailStr
    sso_identity: dict[str, Any] | None = None
    created_at: datetime