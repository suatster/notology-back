import uuid
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .. import models
from dotenv import load_dotenv

load_dotenv()
ACCESS_SECRET = os.getenv('JWT_ACCESS_SECRET')
REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET')
ACCESS_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
REFRESH_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '14'))
ALGORITHM = 'HS256'


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode = {"sub": str(subject), "exp": expire}
    return jwt.encode(to_encode, ACCESS_SECRET, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:  
        return None


def create_refresh_token() -> str:
    return str(uuid.uuid4())


def verify_and_consume_refresh_token( db: Session, token: str) -> models.RefreshToken | None:
    try:
        uuid.UUID(token)
    except ValueError:
        return None
    
    try:
        token_entry = db.query(models.RefreshToken)\
                        .filter(models.RefreshToken.token == token)\
                        .with_for_update(nowait=True)\
                        .one()
    except NoResultFound:
        return None
    except:
        return None

    if token_entry.expires_at < datetime.utcnow():
        return None

    db.delete(token_entry)
    db.commit()

    return token_entry
