from pydantic import BaseModel


class ModelCostBreakdown(BaseModel):
    model: str
    total_cost: float
    request_count: int


class CostAnalytics(BaseModel):
    total_cost: float
    request_count: int
    avg_cost_per_request: float
    by_model: list[ModelCostBreakdown]


class LatencyAnalytics(BaseModel):
    sample_count: int
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float