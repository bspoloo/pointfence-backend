

from app.core.security.security import create_access_token, create_refresh_token, verify_password
from app.db.database import get_db
from app.models.player import Player
from app.schemas.auth import LoginRequest
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user_response import UserResponse

async def login_request(data: LoginRequest, db: Session):

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
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            names=user.names,
            email=user.email,
            player_name=user.player.player_name
        ),
        token_type="bearer"
    )