import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.projects import Project

EMBEDDING_DIM = 1536


class CacheEntry(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "cache_entries"

    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    response: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    project: Mapped["Project"] = relationship(back_populates="cache_entries")