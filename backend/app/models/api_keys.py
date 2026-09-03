import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.projects import Project


class APIKey(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "api_keys"

    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Never store the raw key — only its hash, per PRD security requirements (11.1).
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="api_keys")