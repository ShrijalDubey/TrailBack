from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class Request(BaseModel):
    id: UUID
    project_id: UUID
    model: str
    provider: str
    created_at: datetime
    completed_at: datetime | None = None
    status: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)
    cost: float = Field(ge=0)
    latency: float = Field(ge=0)
    ttft: float = Field(ge=0)

class RoutingDecision(BaseModel):
    request_id: UUID
    candidates: list[str]
    scores: dict[str, float]
    constraints: dict[str, Any]
    selected: str

class Evaluation(BaseModel):
    request_id: UUID
    evaluator: str
    dimensions: dict[str, float]
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
