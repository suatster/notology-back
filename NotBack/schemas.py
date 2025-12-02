from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime


class Config:
    orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

