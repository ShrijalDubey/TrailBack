import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.api_keys import APIKey as APIKeyModel
from app.models.projects import Project as ProjectModel
from app.schemas.api_keys import APIKey as APIKeySchema, APIKeyCreate, APIKeyCreated
from app.utils.security import extract_prefix, generate_api_key, verify_api_key

router = APIRouter(prefix="/v1/api-keys", tags=["api-keys"])


@router.post("", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
def create_api_key(payload: APIKeyCreate, db: Session = Depends(get_db)) -> APIKeyCreated:
    project = db.get(ProjectModel, payload.project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project_id does not reference a real project."
        )

    raw_key, prefix, key_hash = generate_api_key()
    api_key = APIKeyModel(project_id=payload.project_id, key_hash=key_hash, prefix=prefix)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return APIKeyCreated(
        id=api_key.id,
        project_id=api_key.project_id,
        prefix=api_key.prefix,
        api_key=raw_key,
        created_at=api_key.created_at,
    )


@router.get("", response_model=list[APIKeySchema])
def list_api_keys(
    project_id: uuid.UUID = Query(..., description="List keys belonging to this project."),
    db: Session = Depends(get_db),
) -> list[APIKeyModel]:
    if db.get(ProjectModel, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project_id does not reference a real project.")
    return db.query(APIKeyModel).filter(APIKeyModel.project_id == project_id).order_by(APIKeyModel.created_at).all()


@router.get("/{key_id}", response_model=APIKeySchema)
def get_api_key(key_id: uuid.UUID, db: Session = Depends(get_db)) -> APIKeyModel:
    api_key = db.get(APIKeyModel, key_id)
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found.")
    return api_key


@router.delete("/{key_id}", response_model=APIKeySchema)
def revoke_api_key(key_id: uuid.UUID, db: Session = Depends(get_db)) -> APIKeyModel:
    api_key = db.get(APIKeyModel, key_id)
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found.")

    if api_key.revoked_at is None:
        api_key.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(api_key)

    return api_key


def get_current_project(
    x_api_key: str = Header(..., description="RouteAI API key, e.g. tb_xxxxxxxx.<secret>"),
    db: Session = Depends(get_db),) -> ProjectModel:
    prefix = extract_prefix(x_api_key)
    if prefix is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed API key.")


    candidates = db.query(APIKeyModel).filter(APIKeyModel.prefix == prefix).all()

    matched: APIKeyModel | None = None
    for candidate in candidates:
        if verify_api_key(x_api_key, candidate.key_hash):
            matched = candidate
            break

    if matched is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")

    if matched.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This API key has been revoked.")

    project = db.get(ProjectModel, matched.project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key's project no longer exists.")

    return project