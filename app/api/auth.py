from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.base import get_db
from app.services.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=schemas.UserRead,
    status_code=201,
)
def register(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == payload.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Usuário já existe.",
        )

    user = models.User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role or "requester",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/token",
    response_model=schemas.TokenResponse,
)
def login(
    payload: schemas.LoginCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == payload.email)
        .first()
    )

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Usuário inativo.",
        )

    token = create_access_token(user)

    return schemas.TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=schemas.UserRead,
)
def me(
    user: models.User = Depends(get_current_user),
):
    return user
