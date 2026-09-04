from dataclasses import dataclass, field
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.models import (
    Model as ModelORM,
    ModelMetrics as ModelMetricsORM,
    ModelPrice as ModelPriceORM,
    Provider as ProviderORM,
)
from app.schemas.chat import ChatMessage, RouteConstraints

CHARS_PER_TOKEN = 4
DEFAULT_OUTPUT_TOKENS = 256

DEFAULT_METRICS = {
    "gpt-4o":                     {"quality": 0.94, "latency_ms": 900.0},
    "o3-mini":                    {"quality": 0.95, "latency_ms": 1600.0},
    "gpt-4o-mini":                {"quality": 0.82, "latency_ms": 450.0},
    "claude-3-5-sonnet-20241022": {"quality": 0.95, "latency_ms": 1100.0},
    "claude-3-5-haiku-20241022":  {"quality": 0.84, "latency_ms": 550.0},
    "llama-3.3-70b-versatile":    {"quality": 0.88, "latency_ms": 500.0},
    "llama-3.1-8b-instant":       {"quality": 0.76, "latency_ms": 220.0},
    "gemma2-9b-it":               {"quality": 0.74, "latency_ms": 320.0},
}


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


@dataclass
class ModelCandidate:
    model: ModelORM
    provider: ProviderORM
    estimated_cost: float
    predicted_quality: float = 0.80
    predicted_latency_ms: float = 500.0
    score: float = 0.0


@dataclass
class RoutingResult:
    model: ModelORM
    provider: ProviderORM
    estimated_cost: float
    input_tokens: int
    predicted_quality: float
    predicted_latency_ms: float
    candidates_considered: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    ranked_candidates: list[ModelCandidate] = field(default_factory=list)


def get_latest_price(db: Session, model_id) -> ModelPriceORM | None:
    now = datetime.now(timezone.utc)
    return (
        db.query(ModelPriceORM)
        .filter(
            ModelPriceORM.model_id == model_id,
            ModelPriceORM.effective_from <= now,
            or_(ModelPriceORM.effective_to.is_(None), ModelPriceORM.effective_to > now),
        )
        .order_by(ModelPriceORM.effective_from.desc())
        .first()
    )


def calculate_estimated_cost(price: ModelPriceORM | None, input_tokens: int, output_tokens: int) -> float:
    if not price:
        return 0.0
    input_rate = price.prices.get("input_per_1k", 0.0)
    output_rate = price.prices.get("output_per_1k", 0.0)
    return (input_tokens / 1000) * input_rate + (output_tokens / 1000) * output_rate


def get_model_metrics(db: Session, model: ModelORM) -> tuple[float, float]:
    db_metric = (
        db.query(ModelMetricsORM)
        .filter(ModelMetricsORM.model_id == model.id)
        .order_by(ModelMetricsORM.created_at.desc())
        .first()
    )
    if db_metric:
        lat_ms = db_metric.latency * 1000 if db_metric.latency < 50 else db_metric.latency
        return db_metric.quality, lat_ms

    defaults = DEFAULT_METRICS.get(model.name, {"quality": 0.80, "latency_ms": 600.0})
    return defaults["quality"], defaults["latency_ms"]


def select_model(
    db: Session,
    messages: list[ChatMessage],
    constraints: RouteConstraints | None,
    requested_model: str = "auto",
) -> RoutingResult:

    full_prompt = " ".join(m.content for m in messages)
    input_tokens = estimate_tokens(full_prompt)

    all_models = db.query(ModelORM).filter(ModelORM.context_window >= input_tokens).all()
    if not all_models:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No model has a large enough context window for this request.",
        )

    policy = (constraints.policy if constraints else "balanced").lower()

    eligible_candidates: list[ModelCandidate] = []
    for model in all_models:
        price = get_latest_price(db, model.id)
        cost = calculate_estimated_cost(price, input_tokens, DEFAULT_OUTPUT_TOKENS)
        quality, latency_ms = get_model_metrics(db, model)

        if constraints and constraints.budget_usd is not None and cost > constraints.budget_usd:
            continue

        if constraints and constraints.max_latency_ms is not None and latency_ms > constraints.max_latency_ms:
            continue

        if constraints and constraints.min_quality is not None and quality < constraints.min_quality:
            continue

        provider = db.get(ProviderORM, model.provider_id)
        if provider:
            eligible_candidates.append(
                ModelCandidate(
                    model=model,
                    provider=provider,
                    estimated_cost=cost,
                    predicted_quality=quality,
                    predicted_latency_ms=latency_ms,
                )
            )

    if not eligible_candidates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No eligible model fits the requested constraints (budget, latency, or quality floor).",
        )

    _apply_policy_scores(eligible_candidates, policy)

    eligible_candidates.sort(key=lambda c: c.score, reverse=True)

    if requested_model and requested_model != "auto":
        matching = [c for c in eligible_candidates if c.model.name == requested_model]
        others = [c for c in eligible_candidates if c.model.name != requested_model]
        if matching:
            eligible_candidates = matching + others

    primary = eligible_candidates[0]

    return RoutingResult(
        model=primary.model,
        provider=primary.provider,
        estimated_cost=primary.estimated_cost,
        input_tokens=input_tokens,
        predicted_quality=primary.predicted_quality,
        predicted_latency_ms=primary.predicted_latency_ms,
        candidates_considered=[c.model.name for c in eligible_candidates],
        scores={c.model.name: round(c.score, 4) for c in eligible_candidates},
        ranked_candidates=eligible_candidates,
    )


def _apply_policy_scores(candidates: list[ModelCandidate], policy: str) -> None:
    """Calculate and assign the optimization score to each candidate based on policy."""
    if policy == "cheapest":
        max_cost = max(c.estimated_cost for c in candidates) or 1.0
        for c in candidates:
            c.score = round(1.0 - (c.estimated_cost / max_cost), 4)

    elif policy == "fastest":
        max_lat = max(c.predicted_latency_ms for c in candidates) or 1.0
        for c in candidates:
            c.score = round(1.0 - (c.predicted_latency_ms / max_lat), 4)

    elif policy in ("quality", "quality_first"):
        for c in candidates:
            c.score = round(c.predicted_quality, 4)

    else:
        min_cost = min(c.estimated_cost for c in candidates)
        max_cost = max(c.estimated_cost for c in candidates)
        cost_range = max(max_cost - min_cost, 1e-6)

        min_lat = min(c.predicted_latency_ms for c in candidates)
        max_lat = max(c.predicted_latency_ms for c in candidates)
        lat_range = max(max_lat - min_lat, 1e-6)

        for c in candidates:
            cost_norm = 1.0 - ((c.estimated_cost - min_cost) / cost_range)
            lat_norm = 1.0 - ((c.predicted_latency_ms - min_lat) / lat_range)
            quality_norm = c.predicted_quality

            c.score = round(0.45 * quality_norm + 0.35 * cost_norm + 0.20 * lat_norm, 4)