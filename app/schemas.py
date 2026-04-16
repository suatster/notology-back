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


class ChatRequest(BaseModel):
    persona: str
    message: str
    