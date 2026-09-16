

from app.core.security.security import create_access_token, verify_password
from app.db.database import get_db
from app.schemas.auth import LoginRequest
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

async def login_request(data: LoginRequest, db: Session = get_db()):

    user = db.scalar(
        select(User)
        .where(User.email == data.email)
        .where(User.deleted_at.is_(None))
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )