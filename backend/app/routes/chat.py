from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.projects import Project as ProjectORM
from app.models.requests import Request as RequestORM, RoutingDecision as RoutingDecisionORM
from app.routes.api_keys import get_current_project
from app.routing.engine import estimate_tokens, select_model
from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ResponseMessage,
    RoutingMeta,
    Usage,
)

router = APIRouter(prefix="/v1", tags=["gateway"])

_STUB_RESPONSE_CONTENT = "[stub response]"


@router.post("/chat/completions", response_model=ChatCompletionResponse)
def create_chat_completion(
    payload: ChatCompletionRequest,
    project: ProjectORM = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> ChatCompletionResponse:
    routing_result = select_model(db, payload.messages, payload.route)

    output_tokens = estimate_tokens(_STUB_RESPONSE_CONTENT)
    total_tokens = routing_result.input_tokens + output_tokens

    request_row = RequestORM(
        project_id=project.id,
        model_id=routing_result.model.id,
        model=routing_result.model.name,
        provider_id=routing_result.provider.id,
        provider=routing_result.provider.name,
        status="completed",
        input_tokens=routing_result.input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cost=routing_result.estimated_cost,
        latency=0.0, 
        ttft=0.0,
    )
    db.add(request_row)
    db.flush() 

    routing_decision_row = RoutingDecisionORM(
        request_id=request_row.id,
        candidates=routing_result.candidates_considered,
        scores=routing_result.scores,
        constraints=payload.route.model_dump() if payload.route is not None else {},
        selected=routing_result.model.name,
    )
    db.add(routing_decision_row)
    db.commit()
    db.refresh(request_row)

    return ChatCompletionResponse(
        id=request_row.id,
        model=routing_result.model.name,
        provider=routing_result.provider.name,
        choices=[Choice(message=ResponseMessage(content=_STUB_RESPONSE_CONTENT))],
        usage=Usage(
            input_tokens=routing_result.input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        ),
        routing=RoutingMeta(estimated_cost=routing_result.estimated_cost, fallback_used=False),
    )