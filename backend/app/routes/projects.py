import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.schemas.projects import Project as ProjectSchema, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectModel:
    owner = db.get(UserModel, payload.user_id)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_id does not reference a real user.")

    project = ProjectModel(
        user_id=payload.user_id,
        name=payload.name,
        policy_id=payload.policy_id,
        retention=payload.retention,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectSchema])
def list_projects(
    user_id: uuid.UUID | None = Query(default=None, description="Filter to a single owner's projects."),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ProjectModel]:
    q = db.query(ProjectModel)
    if user_id is not None:
        q = q.filter(ProjectModel.user_id == user_id)
    return q.order_by(ProjectModel.created_at).offset(offset).limit(limit).all()


@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)) -> ProjectModel:
    project = db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


@router.patch("/{project_id}", response_model=ProjectSchema)
def update_project(project_id: uuid.UUID, payload: ProjectUpdate, db: Session = Depends(get_db)) -> ProjectModel:
    project = db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    project = db.get(ProjectModel, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    db.delete(project)
    db.commit()