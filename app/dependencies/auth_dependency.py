from fastapi import HTTPException,Cookie, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.auth_service import AuthService


def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = AuthService(db)
    user = service.get_user_from_access_token(access_token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid access token")

    return user
