from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class Model(BaseModel):
    id: UUID
    provider_id: UUID
    name: str
    capabilities: dict[str, Any]
    context_window: int = Field(gt=0)


class ModelPrice(BaseModel):
    model_id: UUID
    prices: dict[str, float]
    effective_from: datetime
    effective_to: datetime | None = None


class ModelMetrics(BaseModel):
    model_id: UUID
    window: str
    latency: float
    ttft: float
    error_rate: float = Field(ge=0, le=1)
    quality: float = Field(ge=0, le=1)