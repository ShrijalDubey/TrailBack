from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProviderCreate(BaseModel):

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=64)


class Provider(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class ModelCreate(BaseModel):
    provider_id: UUID
    name: str = Field(min_length=1, max_length=255)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    context_window: int = Field(gt=0)


class Model(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider_id: UUID
    name: str
    capabilities: dict[str, Any]
    context_window: int = Field(gt=0)


class ModelPriceCreate(BaseModel):
    model_id: UUID
    prices: dict[str, float]
    effective_from: datetime | None = None 
    effective_to: datetime | None = None


class ModelPrice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_id: UUID
    prices: dict[str, float]
    effective_from: datetime
    effective_to: datetime | None = None


class ModelMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    model_id: UUID
    window: str
    latency: float
    ttft: float
    error_rate: float = Field(ge=0, le=1)
    quality: float = Field(ge=0, le=1)