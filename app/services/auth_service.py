from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud
from ..utils.security import hash_password, verify_password
from ..utils.tokens import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_and_consume_refresh_token
)
from ..core.config import settings


class UserAlreadyExists(Exception):
    pass

class MissingRefreshToken(Exception):
    pass

class InvalidOrExpiredRefreshToken(Exception):
    pass


class AuthService:
    
    def __init__(self, db: Session):
        self.db = db


    def register(self, username: str, email: str, password: str):
        if crud.get_user_by_username(self.db, username):
            raise UserAlreadyExists("Username already exists")

        if crud.get_user_by_email(self.db, email):
            raise UserAlreadyExists("Email already exists")

        hashed = hash_password(password)
        user = crud.create_user(self.db, username, email, hashed)
        return user



    def login(self, identifier: str, password: str) -> dict:
        user = (
            crud.get_user_by_username(self.db, identifier)
            or crud.get_user_by_email(self.db, identifier)
        )

        if not user or not verify_password(password, user.hashed_password):
            return None

        access = create_access_token(str(user.id))
        refresh = create_refresh_token()

        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        crud.save_refresh_token(self.db, user.id, refresh, expires_at)

        return {
            "user": user,
            "access": access,
            "refresh": refresh
        }
    


    def get_user_from_access_token(self, access_token: str):
        payload = verify_access_token(access_token)
        if not payload:
            return None

        return crud.get_user_by_id(self.db, payload["sub"])



    def refresh_tokens(self, refresh_token: str) -> dict:
        if not refresh_token:
            raise MissingRefreshToken("Missing refresh token")

        db_rt = verify_and_consume_refresh_token(self.db, refresh_token)
        if not db_rt:
            raise InvalidOrExpiredRefreshToken("Invalid or expired refresh token")

        new_access = create_access_token(str(db_rt.user_id))
        new_refresh = create_refresh_token()

        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        crud.save_refresh_token(
            self.db,
            db_rt.user_id,
            new_refresh,
            expires_at
        )

        return {
            "access": new_access,
            "refresh": new_refresh
        }      
    


    def logout_user(self, user_id: UUID):
        crud.delete_all_refresh_tokens_for_user(self.db, user_id)
