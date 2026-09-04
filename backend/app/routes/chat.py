import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.projects import Project as ProjectORM
from app.models.requests import Request as RequestORM, RoutingDecision as RoutingDecisionORM
from app.providers import ProviderNotConfigured, get_provider
from app.routes.api_keys import get_current_project
from app.routing.engine import ModelCandidate, RoutingResult, select_model
from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ResponseMessage,
    RoutingMeta,
    Usage,
)

router = APIRouter(prefix="/v1", tags=["gateway"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
def create_chat_completion(
    payload: ChatCompletionRequest,
    project: ProjectORM = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> ChatCompletionResponse:

    routing_result = select_model(
        db=db,
        messages=payload.messages,
        constraints=payload.route,
        requested_model=payload.model,
    )

    messages_raw = [{"role": m.role, "content": m.content} for m in payload.messages]

    call_result = _execute_with_fallback(routing_result.ranked_candidates, messages_raw)

    if not call_result["success"]:
        _save_request_record(
            db=db,
            project=project,
            routing_result=routing_result,
            payload=payload,
            status_str="failed",
            chosen_candidate=call_result["candidate"],
            latency=call_result["total_latency"],
        )
        raise HTTPException(
            status_code=call_result["http_status"],
            detail=call_result["error_message"],
        )

    winning_adapter = call_result["adapter"]
    provider_resp = call_result["response"]
    winning_candidate = call_result["candidate"]

    actual_cost = winning_adapter.estimate_cost(
        input_tokens=provider_resp.input_tokens,
        output_tokens=provider_resp.output_tokens,
        model=provider_resp.model,
    )

    request_row = _save_request_record(
        db=db,
        project=project,
        routing_result=routing_result,
        payload=payload,
        status_str="completed",
        chosen_candidate=winning_candidate,
        latency=call_result["total_latency"],
        input_tokens=provider_resp.input_tokens,
        output_tokens=provider_resp.output_tokens,
        total_tokens=provider_resp.total_tokens,
        cost=actual_cost,
    )

    return ChatCompletionResponse(
        id=request_row.id,
        model=provider_resp.model,
        provider=winning_candidate.provider.name,
        choices=[Choice(message=ResponseMessage(content=provider_resp.content))],
        usage=Usage(
            input_tokens=provider_resp.input_tokens,
            output_tokens=provider_resp.output_tokens,
            total_tokens=provider_resp.total_tokens,
        ),
        routing=RoutingMeta(
            estimated_cost=actual_cost,
            fallback_used=call_result["fallback_used"],
            fallback_reason=call_result["fallback_reason"],
            fallbacks_attempted=call_result["fallbacks_attempted"],
        ),
    )


def _execute_with_fallback(candidates: list[ModelCandidate], messages: list[dict]) -> dict:

    fallbacks_attempted = []
    total_latency = 0.0

    for idx, candidate in enumerate(candidates):
        try:
            adapter = get_provider(candidate.provider.slug)
        except ProviderNotConfigured as exc:
            fallbacks_attempted.append(f"{candidate.model.name}: Provider not configured ({exc})")
            continue

        start_time = time.time()
        try:
            response = adapter.chat(messages=messages, model=candidate.model.name)
            elapsed = time.time() - start_time
            total_latency += elapsed

            fallback_used = idx > 0
            fallback_reason = fallbacks_attempted[-1] if fallback_used else None

            return {
                "success": True,
                "candidate": candidate,
                "adapter": adapter,
                "response": response,
                "total_latency": total_latency,
                "fallback_used": fallback_used,
                "fallback_reason": fallback_reason,
                "fallbacks_attempted": fallbacks_attempted,
            }

        except Exception as exc:
            elapsed = time.time() - start_time
            total_latency += elapsed

            error = adapter.normalize_error(exc)
            failure_note = f"{candidate.model.name} failed ({error.category}, status {error.http_status}): {error.message}"
            fallbacks_attempted.append(failure_note)

            has_more_candidates = idx < len(candidates) - 1

            if error.retryable and has_more_candidates:
                continue

            return {
                "success": False,
                "candidate": candidate,
                "adapter": adapter,
                "http_status": error.http_status,
                "error_message": error.message,
                "total_latency": total_latency,
                "fallbacks_attempted": fallbacks_attempted,
            }

    return {
        "success": False,
        "candidate": candidates[0],
        "adapter": None,
        "http_status": status.HTTP_503_SERVICE_UNAVAILABLE,
        "error_message": f"No available providers: {', '.join(fallbacks_attempted)}",
        "total_latency": total_latency,
        "fallbacks_attempted": fallbacks_attempted,
    }


def _save_request_record(
    db: Session,
    project: ProjectORM,
    routing_result: RoutingResult,
    payload: ChatCompletionRequest,
    status_str: str,
    chosen_candidate: ModelCandidate,
    latency: float = 0.0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
    cost: float = 0.0,
) -> RequestORM:
    """Save Request and RoutingDecision rows in the database for observability and audit."""
    request_row = RequestORM(
        project_id=project.id,
        model_id=chosen_candidate.model.id,
        model=chosen_candidate.model.name,
        provider_id=chosen_candidate.provider.id,
        provider=chosen_candidate.provider.name,
        status=status_str,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cost=cost,
        latency=round(latency, 4),
        ttft=0.0,
    )
    db.add(request_row)
    db.flush()

    routing_decision_row = RoutingDecisionORM(
        request_id=request_row.id,
        candidates=routing_result.candidates_considered,
        scores=routing_result.scores,
        constraints=payload.route.model_dump() if payload.route else {},
        selected=chosen_candidate.model.name,
    )
    db.add(routing_decision_row)
    db.commit()
    db.refresh(request_row)

    return request_row