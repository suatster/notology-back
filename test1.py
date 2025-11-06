from fastapi import FastAPI
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "a?s2uxc3!acbvts^xyt?a"  # bunu güçlü rastgele bir string yap
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class User(BaseModel):
    email : EmailStr
    password : str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

users = [
    {"email": "suatinator@gmail.com", "password": "Burak123", "id": "1"},  
    {"email": "gurhanaras@gmail.com", "password": "Gurhan456", "id": "2"},
    {"email": "fakeuser@gmail.com", "password": "Gurhan456", "id": "3"}
]

# delete password and insert hashed form of the password into users
for u in users:
    hashed = hash_password(u['password'])
    u.pop("password")
    u["hashed_password"] = hashed

# print(users[0]['hashed_password']) # $2b$12$uaBQhvzBUS/MTw18wNeZfOEvFh4/gLIjv5X4A0xBn6cCrkQveJWMa
# print(users[1]['hashed_password']) # $2b$12$PbVWnuP0MSqhnGPaVvekVu6yd2wyZC4A4JVF5xSiNbV.bCcxiloWa
# print(users[2]['hashed_password']) # $2b$12$7tw1Z.Y08zDl.3Nn/Qko5.t5MRhhOOeBjGOQpwnxqpeQQBS3e0/0y

next_id = 4

def create_user(email :str, password : str):
    global next_id 
    hashed = hash_password(password)
    user = {
        "id": next_id,
        "email": email,
        "hashed_password": hashed
    }
    users.append(user)
    next_id += 1
    return user

@app.post("/register", status_code=status.HTTP_201_CREATED)
def sign_up(user: User):
    new_user = create_user(user.email, user.password)
    return {"message": "You successfully registered. Welcome!"}


def find_user(email: str, user: UserLogin):
    found_user = None
    for u in users:
        if u["email"] == email:
            found_user = u   
            break

    if not found_user:        
        raise HTTPException(status_code=404, detail="User was not found.")
    
    if not verify_password(user.password, found_user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
    return found_user

@app.post("/login")
def login(user: UserLogin):
    found_user = find_user(user.email, user)
    return {"message": "Login successful."}

# https://gurhanaras1665-8755416.postman.co/workspace/G%C3%BCrhan-Aras's-Workspace~965f9191-0a64-4e12-81e0-fb30f43a5a6b/collection/49735711-14c9f16d-cfbc-406b-b944-d8166e80e4cc?action=share&creator=49735711
