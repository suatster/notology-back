from sqlalchemy.orm import Session
from datetime import datetime
from . import models

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = models.User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()


def save_refresh_token(db: Session, user_id, token: str, expires_at: datetime):
    rt = models.RefreshToken(user_id=user_id, token=token, expires_at=expires_at, created_at=datetime.utcnow())
    db.add(rt)
    db.commit()
    db.refresh(rt)


def delete_refresh_token(db: Session, token: str):
    rt = get_refresh_token(db, token)
    if rt:
        db.delete(rt)
        db.commit()


def delete_all_refresh_tokens_for_user(db: Session, user_id):
    db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user_id).delete()
    db.commit()
    