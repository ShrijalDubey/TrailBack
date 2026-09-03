from typing import Any, TYPE_CHECKING
import uuid

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.projects import Project


class User(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    sso_identity: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")