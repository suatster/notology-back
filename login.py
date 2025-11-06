from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets

app = FastAPI()


# ---------------------------
# Şifre hashleme ayarları
# ---------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str,) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------
# JWT ayarları
# ---------------------------

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    expire_ts = int(expire.timestamp())  # datetime -> integer timestamp (JWT datetime tipini anlamaz.)
    to_encode.update({"exp": expire_ts})  # JWT exp alanına integer ver
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ---------------------------
# Modeller
# ---------------------------

class User(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------------------------
# Kullanıcı veri tabanı
# ---------------------------

users = [
    {"email": "suatinator@gmail.com", "username": "Suatinator", "password": "Burak123", "id": 1},
    {"email": "gurhanaras@gmail.com", "username": "Gurhan", "password": "Gurhan456", "id": 2},
    {"email": "fakeuser@gmail.com", "username": "FakeUser", "password": "Gurhan456", "id": 3}
]

for u in users:
    hashed = hash_password(u["password"])    
    u.pop("password")
    u["hashed_password"] = hashed

next_id = 4


# ---------------------------
# Kullanıcı oluşturma
# ---------------------------

def create_user(email: str, password: str, username: str):
    global next_id

    # Email veya username benzersizliği kontrolü
    if any(u["email"] == email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if any(u["username"] == username for u in users):
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    hashed = hash_password(password)

    user = {
        "id": next_id,
        "email": email,
        "username": username,
        "hashed_password": hashed
    } 
    
    users.append(user)
    next_id += 1
    return user


@app.post("/register", status_code=status.HTTP_201_CREATED)
def sign_up(user: User):
    new_user = create_user(user.email, user.password, user.username)
    return {
        "message": f"User {new_user['username']} registered successfully!",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "username": new_user["username"]
        }
    }


# ---------------------------
# Kullanıcı bulma ve şifre doğrulama
# ---------------------------

def find_user(email: str, user: UserLogin):
    found_user = None
    for u in users:
        if u["email"] == email:
            found_user = u
        
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found.")

    if not verify_password(user.password, found_user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")       
    
    return found_user


# ---------------------------
# Login
# ---------------------------

@app.post("/login")
def login(user: UserLogin):
    found_user = find_user(user.email, user)

    # Token oluştur
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": found_user["email"]},
        expires_delta=access_token_expires
    )

    return {
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer"
    }


# CORS Ayarları
# header
# cookies
# public - protected Endpoint
# JSON Web Token (JWT)       
# @router
# database connection (ORM-Object Relational Mapping)
# sqlalchemy

#email validation

# https://gurhanaras1665-8755416.postman.co/workspace/G%C3%BCrhan-Aras's-Workspace~965f9191-0a64-4e12-81e0-fb30f43a5a6b/collection/49735711-908a5118-74f3-44f5-b34c-c71686211876?action=share&creator=49735711

