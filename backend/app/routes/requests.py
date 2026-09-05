import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.projects import Project as ProjectORM
from app.models.requests import Request as RequestORM, RoutingDecision as RoutingDecisionORM
from app.routes.api_keys import get_current_project
from app.schemas.requests import Request as RequestSchema, RequestDetail, RoutingDecision as RoutingDecisionSchema

router = APIRouter(prefix="/v1/requests", tags=["requests"])


@router.get("", response_model=list[RequestSchema])
def list_requests(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    project: ProjectORM = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> list[RequestORM]:
    q = db.query(RequestORM).filter(RequestORM.project_id == project.id)
    if status_filter is not None:
        q = q.filter(RequestORM.status == status_filter)
    return q.order_by(RequestORM.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{request_id}", response_model=RequestDetail)
def get_request(
    request_id: uuid.UUID,
    project: ProjectORM = Depends(get_current_project),
    db: Session = Depends(get_db),
) -> RequestDetail:
    request_row = db.get(RequestORM, request_id)
    if request_row is None or request_row.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

    routing_decision = (
        db.query(RoutingDecisionORM).filter(RoutingDecisionORM.request_id == request_id).first()
    )

    return RequestDetail(
        **RequestSchema.model_validate(request_row).model_dump(),
        routing_decision=RoutingDecisionSchema.model_validate(routing_decision) if routing_decision else None,
    )