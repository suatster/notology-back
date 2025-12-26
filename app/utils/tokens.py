import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta
from jose import jwt, JWTError
from .. import models
from app.core.config import settings


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(
        payload, 
        settings.JWT_ACCESS_SECRET, 
        algorithm=settings.ALGORITHM
    )


def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_ACCESS_SECRET, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:  
        return None


def create_refresh_token() -> str:
    return str(uuid.uuid4())


def verify_and_consume_refresh_token(
        db: Session,
        token: str
    ) -> models.RefreshToken | None:
    
    try:
        str(uuid.UUID(token))
    except ValueError:
        return None
    
    try:
        token_entry = (
            db.query(models.RefreshToken) 
            .filter(models.RefreshToken.token == token) 
            .with_for_update(nowait=True) 
            .one()
        )
    except (NoResultFound, Exception):
        return None

    if token_entry.expires_at < datetime.utcnow():
        db.delete(token_entry)
        db.commit()
        return None

    db.delete(token_entry)
    db.commit()

    return token_entry
