from fastapi import (APIRouter, Depends, 
        HTTPException, Response, Cookie, Request)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import crud, schemas
from ..database import get_db
from ..utils.security import hash_password, verify_password
from ..utils.tokens import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_and_consume_refresh_token
)
from dotenv import load_dotenv
import os


router = APIRouter(prefix="/auth", tags=["Auth"])


load_dotenv()
ACCESS_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
REFRESH_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '14'))
FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173')



@router.post("/register", response_model=schemas.RegisterResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed = hash_password(payload.password)
    user = crud.create_user(db, payload.username, payload.email, hashed)
    
    return schemas.RegisterResponse(
        message="You successfully registered", 
        user=user
    )


@router.post("/login")
def token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)  # redirection kullanıcı başkalarının bilgisine erişmek isterse logine yönlendir tekrardan 
):
    
    user = (crud.get_user_by_username(db, form_data.username) 
           or crud.get_user_by_email(db, form_data.username))
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token()

    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    crud.save_refresh_token(db, user.id, refresh, expires_at)

    response.set_cookie(key="access_token", value=access, httponly=True, samesite="lax",
                        path="/", max_age=ACCESS_EXPIRE_MINUTES * 60)
    response.set_cookie(key="refresh_token", value=refresh, httponly=True, samesite="lax",
                        path="/", max_age=REFRESH_EXPIRE_DAYS * 24* 60 * 60)

    return {"message": "Login successful"}



def get_current_user(
    request: Request,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    
    origin = request.headers.get("origin")
    if origin and origin != FRONTEND_ORIGIN:
        raise HTTPException(status_code=403)

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user = crud.get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user



@router.get("/me", response_model=schemas.User)
def me(current_user: schemas.User = Depends(get_current_user)):
    return current_user



@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    db_rt = verify_and_consume_refresh_token(db, refresh_token)
        
    if not db_rt:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access = create_access_token(str(db_rt.user_id))
    new_refresh = create_refresh_token()

    expires_at = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    crud.save_refresh_token(db, db_rt.user_id, new_refresh, expires_at)

    response.set_cookie("access_token", new_access, httponly=True, samesite="lax", 
                        path="/", max_age=ACCESS_EXPIRE_MINUTES * 60)
    response.set_cookie("refresh_token", new_refresh, httponly=True, samesite="lax", 
                        path="/", max_age=REFRESH_EXPIRE_DAYS * 24 * 60 * 60)

    return {"token_type": "bearer"}



@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  
):
    
    crud.delete_all_refresh_tokens_for_user(db, current_user.id)

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return {"message": "You successfully logged out"}
