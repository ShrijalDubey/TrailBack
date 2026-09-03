import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.api_keys import APIKey
    from app.models.requests import Request
    from app.models.cache_entries import CacheEntry


class Project(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    policy_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    retention: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (CheckConstraint("retention >= 0", name="ck_project_retention_nonneg"),)

    user: Mapped["User"] = relationship(back_populates="projects")
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    requests: Mapped[list["Request"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    cache_entries: Mapped[list["CacheEntry"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    budgets: Mapped[list["Budget"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Budget(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "budgets"

    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "monthly", "daily"
    limit: Mapped[float] = mapped_column(Float, nullable=False)
    current_spend: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("\"limit\" >= 0", name="ck_budget_limit_nonneg"),
        CheckConstraint("current_spend >= 0", name="ck_budget_spend_nonneg"),
    )

    project: Mapped["Project"] = relationship(back_populates="budgets")


class Alert(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "alerts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (CheckConstraint("threshold >= 0", name="ck_alert_threshold_nonneg"),)

    project: Mapped["Project"] = relationship(back_populates="alerts")