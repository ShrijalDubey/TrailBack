import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.users import User as UserModel
from app.schemas.users import User as UserSchema, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserModel:
    existing = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with that email already exists.")

    user = UserModel(email=payload.email, sso_identity=payload.sso_identity)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserSchema])
def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[UserModel]:
    return db.query(UserModel).order_by(UserModel.created_at).offset(offset).limit(limit).all()


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserModel:
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=UserSchema)
def update_user(user_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db)) -> UserModel:
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    updates = payload.model_dump(exclude_unset=True) 

    if "email" in updates and updates["email"] != user.email:
        clash = db.query(UserModel).filter(UserModel.email == updates["email"], UserModel.id != user_id).first()
        if clash is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="A user with that email already exists."
            )

    for field, value in updates.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    user = db.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.delete(user)
    db.commit()