import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.projects import Project


class Request(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "requests"

    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    model_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="SET NULL"), nullable=True, index=True
    )
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("providers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    provider: Mapped[str] = mapped_column(String(255), nullable=False)

    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)

    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    latency: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    ttft: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("input_tokens >= 0", name="ck_request_input_tokens_nonneg"),
        CheckConstraint("output_tokens >= 0", name="ck_request_output_tokens_nonneg"),
        CheckConstraint("total_tokens >= 0", name="ck_request_total_tokens_nonneg"),
        CheckConstraint("cost >= 0", name="ck_request_cost_nonneg"),
        CheckConstraint("latency >= 0", name="ck_request_latency_nonneg"),
        CheckConstraint("ttft >= 0", name="ck_request_ttft_nonneg"),
    )

    project: Mapped["Project"] = relationship(back_populates="requests")
    routing_decision: Mapped["RoutingDecision | None"] = relationship(
        back_populates="request", cascade="all, delete-orphan", uselist=False
    )
    evaluation: Mapped["Evaluation | None"] = relationship(
        back_populates="request", cascade="all, delete-orphan", uselist=False
    )


class RoutingDecision(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "routing_decisions"

    request_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    candidates: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    scores: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    constraints: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    selected: Mapped[str] = mapped_column(String(255), nullable=False)

    request: Mapped["Request"] = relationship(back_populates="routing_decision")


class Evaluation(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "evaluations"

    request_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    evaluator: Mapped[str] = mapped_column(String(255), nullable=False)
    dimensions: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 1", name="ck_evaluation_score_range"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_evaluation_confidence_range"),
    )

    request: Mapped["Request"] = relationship(back_populates="evaluation")