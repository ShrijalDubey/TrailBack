import math

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.projects import Project as ProjectORM
from app.models.requests import Request as RequestORM
from app.routes.api_keys import get_current_project
from app.schemas.analytics import CostAnalytics, LatencyAnalytics, ModelCostBreakdown

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = max(0, math.ceil(p * len(sorted_values)) - 1)
    return sorted_values[min(idx, len(sorted_values) - 1)]


@router.get("/cost", response_model=CostAnalytics)
def cost_analytics(
    project: ProjectORM = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> CostAnalytics:
    totals = (
        db.query(func.coalesce(func.sum(RequestORM.cost), 0.0), func.count(RequestORM.id))
        .filter(RequestORM.project_id == project.id)
        .one()
    )
    total_cost, request_count = totals

    by_model_rows = (
        db.query(RequestORM.model, func.sum(RequestORM.cost), func.count(RequestORM.id))
        .filter(RequestORM.project_id == project.id)
        .group_by(RequestORM.model)
        .order_by(func.sum(RequestORM.cost).desc())
        .all()
    )

    return CostAnalytics(
        total_cost=total_cost,
        request_count=request_count,
        avg_cost_per_request=(total_cost / request_count) if request_count else 0.0,
        by_model=[
            ModelCostBreakdown(model=model, total_cost=cost, request_count=count)
            for model, cost, count in by_model_rows
        ],
    )


@router.get("/latency", response_model=LatencyAnalytics)
def latency_analytics(
    project: ProjectORM = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> LatencyAnalytics:
    rows = (
        db.query(RequestORM.latency)
        .filter(RequestORM.project_id == project.id, RequestORM.status == "completed")
        .all()
    )
    values = sorted(r[0] for r in rows)

    if not values:
        return LatencyAnalytics(sample_count=0, avg_latency=0.0, p50_latency=0.0, p95_latency=0.0, p99_latency=0.0)

    return LatencyAnalytics(
        sample_count=len(values),
        avg_latency=sum(values) / len(values),
        p50_latency=_percentile(values, 0.50),
        p95_latency=_percentile(values, 0.95),
        p99_latency=_percentile(values, 0.99),
    )