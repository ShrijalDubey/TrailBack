from dataclasses import dataclass, field
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.models import Model as ModelORM, ModelPrice as ModelPriceORM, Provider as ProviderORM
from app.schemas.chat import ChatMessage, RouteConstraints


_CHARS_PER_TOKEN_ESTIMATE = 4


_ASSUMED_OUTPUT_TOKENS_FOR_ESTIMATE = 256


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // _CHARS_PER_TOKEN_ESTIMATE)


@dataclass
class RoutingResult:
    model: ModelORM
    provider: ProviderORM
    estimated_cost: float
    input_tokens: int
    candidates_considered: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)


def _latest_price(db: Session, model_id) -> ModelPriceORM | None:
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


def _estimate_cost(price: ModelPriceORM | None, input_tokens: int, output_tokens: int) -> float:
    if price is None:

        return 0.0
    input_rate = price.prices.get("input_per_1k", 0.0)
    output_rate = price.prices.get("output_per_1k", 0.0)
    return (input_tokens / 1000) * input_rate + (output_tokens / 1000) * output_rate


def select_model(db: Session, messages: list[ChatMessage], constraints: RouteConstraints | None) -> RoutingResult:
    """
    Deterministic MVP router (PRD section 7: "start deterministic, introduce
    ML only after sufficient data exists"). Policy support is limited to
    "cheapest" for now -- the only one meaningful without quality/latency
    telemetry, which no model has yet since nothing's been benchmarked.
    """
    input_tokens = estimate_tokens(" ".join(m.content for m in messages))

    eligible = db.query(ModelORM).filter(ModelORM.context_window >= input_tokens).all()

    if not eligible:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No model has a large enough context window for this request.",
        )

    scored: list[tuple[ModelORM, float]] = []
    for model in eligible:
        price = _latest_price(db, model.id)
        cost = _estimate_cost(price, input_tokens, _ASSUMED_OUTPUT_TOKENS_FOR_ESTIMATE)

        if constraints is not None and constraints.budget_usd is not None and cost > constraints.budget_usd:
            continue 

        scored.append((model, cost))

    if not scored:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No eligible model fits the given budget_usd constraint.",
        )

    scored.sort(key=lambda pair: (pair[1], pair[0].name))
    selected_model, selected_cost = scored[0]

    provider = db.get(ProviderORM, selected_model.provider_id)

    return RoutingResult(
        model=selected_model,
        provider=provider,
        estimated_cost=selected_cost,
        input_tokens=input_tokens,
        candidates_considered=[m.name for m, _ in scored],
        scores={m.name: c for m, c in scored},
    )