from fastapi import FastAPI 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Depends, status, Cookie, Response
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import secrets
from .models import User
from . import utility

app = FastAPI()


# ---------------------------
# CORS ayarları
# ---------------------------

app.add_middleware (
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True # Cookie veya Authorization header’ı gönderilebilir.
)


# ---------------------------
# JWT ayarları
# ---------------------------

SECRET_KEY = "axasdmcbxgkfsrlfsf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 500
REFRESH_TOKEN_EXPIRE_DAYS = 7


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---------------------------
# Kullanıcı veri tabanı
# ---------------------------

users: List[dict] = [
    {"email": "suatinator@gmail.com", "username": "Suatinator", "password": "Burak123", "id": 1},
    {"email": "gurhanaras@gmail.com", "username": "Gurhan", "password": "Gurhan456", "id": 2},
    {"email": "fakeuser@gmail.com", "username": "FakeUser", "password": "Gurhan456", "id": 3}
]

for u in users:
    hashed = utility.hash_password(u["password"])    
    u.pop("password")
    u["hashed_password"] = hashed

next_id = 4


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError("Token payload invalid")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")


# ---------------------------
# Kullanıcı oluşturma
# ---------------------------

def create_user(email: str, password: str, username: str):
    global next_id
    if any(u["email"] == email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if any(u["username"] == username for u in users):
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    hashed = utility.hash_password(password)
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
# Login
# ---------------------------

@app.post("/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = next((u for u in users if u["email"] == form_data.username), None)
    
    if not user or not utility.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
 
    access_token = create_token({"sub": user["email"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token({"sub": user["email"]}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    response.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax")
    
    return {"message": "Login successful", "access_token": access_token, "refresh_token": refresh_token}



# ---------------------------
# Current User 
# ---------------------------

@app.get("/me")
def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session")
    
    email = decode_token(access_token)
    
    user = next((u for u in users if u["email"] == email), None)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user["id"], "email": user["email"], "username": user["username"]}


@app.post("/refresh")
def refresh_token(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    email = decode_token(refresh_token)
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_access_token = create_token({"sub": email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie("access_token", new_access_token, httponly=True, secure=False, samesite="lax")
    return {"access_token": new_access_token}




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

