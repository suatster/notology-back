from pydantic import BaseModel, EmailStr

# ---------------------------
# Modeller
# ---------------------------

class User(BaseModel):
    email: EmailStr
    password: str
    username: str


