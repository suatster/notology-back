from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4, UUID
from . import models

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = models.Users(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.Users).filter(models.Users.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).filter(models.Users.email == email).first()


def get_user_by_id(db: Session, user_id):
    return db.query(models.Users).filter(models.Users.id == user_id).first()


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


def create_image(db: Session,id: UUID, user_id: str, file_path: str, file_type: str) -> models.Images:
    image = models.Images(
        id=id,
        user_id=user_id,
        file_path=file_path,
        file_type=file_type
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image



# def get_last_images_for_user(db: Session, user_id: str, limit: int = 5):
#    return (
#        db.query(models.Images)
#        .filter(models.Images.user_id == user_id)
#        .order_by(models.Images.created_at.desc())  # created_at’a göre ters sırala
#        .limit(limit)  # sadece 5 kayıt al
#        .all()
#    )