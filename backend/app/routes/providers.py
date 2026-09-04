import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.models import Provider as ProviderModel
from app.schemas.models import Provider as ProviderSchema, ProviderCreate

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("", response_model=ProviderSchema, status_code=status.HTTP_201_CREATED)
def create_provider(payload: ProviderCreate, db: Session = Depends(get_db)) -> ProviderModel:
    existing = db.query(ProviderModel).filter(
        (ProviderModel.name == payload.name) | (ProviderModel.slug == payload.slug)
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A provider with that name or slug already exists.",
        )

    provider = ProviderModel(name=payload.name, slug=payload.slug)
    db.add(provider)
    db.commit()
    db.refresh(provider) 
    return provider


@router.get("", response_model=list[ProviderSchema])
def list_providers(db: Session = Depends(get_db)) -> list[ProviderModel]:
    return db.query(ProviderModel).order_by(ProviderModel.name).all()


@router.get("/{provider_id}", response_model=ProviderSchema)
def get_provider(provider_id: uuid.UUID, db: Session = Depends(get_db)) -> ProviderModel:
    provider = db.get(ProviderModel, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")
    return provider