from sqlalchemy.orm import Session
from pydantic import EmailStr
from datetime import datetime
from . import models

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = models.Users(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.Users).filter(models.Users.username == username).first()


def get_user_by_email(db: Session, email: EmailStr):
    return db.query(models.Users).filter(models.Users.email == email).first()


def get_user_by_id(db: Session, user_id):
    return db.query(models.Users).filter(models.Users.id == user_id).first()


def save_refresh_token(db: Session, user_id, token: str, expires_at: datetime):
    rt = models.RefreshToken(user_id=user_id, token=token, expires_at=expires_at, created_at=datetime.utcnow())
    db.add(rt)
    db.commit()
    db.refresh(rt)


def delete_all_refresh_tokens_for_user(db: Session, user_id):
    db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user_id).delete()
    db.commit()
