from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from app.core.config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY
import jwt


password_hash = PasswordHash.recommended()

def hash_password(password:str):
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str)-> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.decode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )