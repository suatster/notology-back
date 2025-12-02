import uuid
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv


load_dotenv()
ACCESS_SECRET = os.getenv('JWT_ACCESS_SECRET')
REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET')
ACCESS_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
REFRESH_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '14'))
ALGORITHM = 'HS256'


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode = {"sub":  str(subject), "exp": expire}
    return jwt.encode(to_encode, ACCESS_SECRET, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_refresh_token() -> str:
    return str(uuid.uuid4())


def verify_refresh_token(token: str) -> dict | None:
    return None
