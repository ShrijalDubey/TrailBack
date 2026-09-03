import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin


class Provider(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "providers"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    models: Mapped[list["Model"]] = relationship(back_populates="provider", cascade="all, delete-orphan")


class Model(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "models"

    provider_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    context_window: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (CheckConstraint("context_window > 0", name="ck_model_context_window_positive"),)

    provider: Mapped["Provider"] = relationship(back_populates="models")
    prices: Mapped[list["ModelPrice"]] = relationship(back_populates="model", cascade="all, delete-orphan")
    metrics: Mapped[list["ModelMetrics"]] = relationship(back_populates="model", cascade="all, delete-orphan")


class ModelPrice(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "model_prices"

    model_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prices: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    model: Mapped["Model"] = relationship(back_populates="prices")


class ModelMetrics(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "model_metrics"

    model_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    window: Mapped[str] = mapped_column(String(32), nullable=False)
    latency: Mapped[float] = mapped_column(Float, nullable=False)
    ttft: Mapped[float] = mapped_column(Float, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False)
    quality: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("error_rate >= 0 AND error_rate <= 1", name="ck_model_metrics_error_rate_range"),
        CheckConstraint("quality >= 0 AND quality <= 1", name="ck_model_metrics_quality_range"),
    )

    model: Mapped["Model"] = relationship(back_populates="metrics")