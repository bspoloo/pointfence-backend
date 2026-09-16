from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError

from app.db.database import get_db
from app.models.player import Player
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
password_hash = PasswordHash.recommended()

def hash_password(password:str):
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str)-> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(user: User):
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "exp": expire,
        "user": {
            "names": user.names,
            "email": user.email,
            "player_name": user.player.player_name
        }
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

def create_refresh_token(user: User):
    expire = datetime.now(timezone.utc) + timedelta(minutes=(JWT_ACCESS_TOKEN_EXPIRE_MINUTES + 30))
    payload = {
        "sub": str(user.id),
        "exp": expire,
        "user": {
            "names": user.names,
            "email": user.email,
            "player_name": user.player.player_name
        }
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        return int(user_id)

    except (InvalidTokenError, ValueError):
        raise credentials_exception

def get_current_user(user_id: int = Depends(get_current_user_id),db: Session = Depends(get_db)) -> User:

    user = db.scalar(
        select(User)
        .where(User.id == user_id)
        .where(User.deleted_at.is_(None))
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user