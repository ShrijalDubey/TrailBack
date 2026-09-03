import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.mixins import UUIDPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.models import Model


class Benchmark(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "benchmarks"

    dataset: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")

    results: Mapped[list["BenchmarkResult"]] = relationship(
        back_populates="benchmark", cascade="all, delete-orphan"
    )


class BenchmarkResult(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "benchmark_results"

    benchmark_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("benchmarks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    latency: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("score >= 0", name="ck_benchmark_result_score_nonneg"),
        CheckConstraint("cost >= 0", name="ck_benchmark_result_cost_nonneg"),
        CheckConstraint("latency >= 0", name="ck_benchmark_result_latency_nonneg"),
    )

    benchmark: Mapped["Benchmark"] = relationship(back_populates="results")
    model: Mapped["Model"] = relationship()