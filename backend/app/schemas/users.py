from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    sso_identity: dict[str, Any] | None = None


class UserUpdate(BaseModel):

    email: EmailStr | None = None
    sso_identity: dict[str, Any] | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    sso_identity: dict[str, Any] | None = None
    created_at: datetime