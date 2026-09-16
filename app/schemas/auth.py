from pydantic import BaseModel, EmailStr

from app.schemas.user_response import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse
    token_type: str = "bearer"