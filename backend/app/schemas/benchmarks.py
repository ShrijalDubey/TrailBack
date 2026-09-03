from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Benchmark(BaseModel):
    id: UUID
    dataset: str
    version: str
    status: str
    created_at: datetime


class BenchmarkResult(BaseModel):
    id: UUID
    benchmark_id: UUID
    model_id: UUID
    task: str

    score: float = Field(ge=0)
    cost: float = Field(ge=0)
    latency: float = Field(ge=0)