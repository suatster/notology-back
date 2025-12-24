from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class User(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True    


class RegisterResponse(BaseModel):
    message: str
    user: User


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class ImageResponse(BaseModel):
    id: UUID
    file_path: str
    file_type: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True
        