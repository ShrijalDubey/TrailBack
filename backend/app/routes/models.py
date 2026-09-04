import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.models import Model as ModelORM, ModelPrice as ModelPriceORM, Provider as ProviderORM
from app.schemas.models import (
    Model as ModelSchema,
    ModelCreate,
    ModelPrice as ModelPriceSchema,
    ModelPriceCreate,
)

router = APIRouter(prefix="/models", tags=["models"])


@router.post("", response_model=ModelSchema, status_code=status.HTTP_201_CREATED)
def create_model(payload: ModelCreate, db: Session = Depends(get_db)) -> ModelORM:
    if db.get(ProviderORM, payload.provider_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="provider_id does not reference a real provider."
        )

    model = ModelORM(
        provider_id=payload.provider_id,
        name=payload.name,
        capabilities=payload.capabilities,
        context_window=payload.context_window,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.get("", response_model=list[ModelSchema])
def list_models(
    provider_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ModelORM]:
    q = db.query(ModelORM)
    if provider_id is not None:
        q = q.filter(ModelORM.provider_id == provider_id)
    return q.order_by(ModelORM.name).all()


@router.get("/{model_id}", response_model=ModelSchema)
def get_model(model_id: uuid.UUID, db: Session = Depends(get_db)) -> ModelORM:
    model = db.get(ModelORM, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found.")
    return model


@router.post("/{model_id}/prices", response_model=ModelPriceSchema, status_code=status.HTTP_201_CREATED)
def add_model_price(model_id: uuid.UUID, payload: ModelPriceCreate, db: Session = Depends(get_db)) -> ModelPriceORM:
    if db.get(ModelORM, model_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found.")
    if payload.model_id != model_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="model_id in body must match the URL.")

    price = ModelPriceORM(
        model_id=model_id,
        prices=payload.prices,
        effective_from=payload.effective_from or datetime.now(timezone.utc),
        effective_to=payload.effective_to,
    )
    db.add(price)
    db.commit()
    db.refresh(price)
    return price