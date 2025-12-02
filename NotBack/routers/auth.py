from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import crud, schemas, models
from ..database import get_db
from ..utils.security import hash_password, verify_password
from ..utils.tokens import create_access_token, create_refresh_token, verify_access_token, verify_refresh_token


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post('/register', response_model=schemas.UserOut)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, payload.username) or crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    hashed = hash_password(payload.password)
    user = crud.create_user(db, payload.username, payload.email, hashed)
    return user



@router.post('/login')
def token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username) or crud.get_user_by_email(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token()

    expires_at = datetime.utcnow() + timedelta(days=14)
    crud.save_refresh_token(db, user.id, refresh, expires_at)

    response.set_cookie(key='access_token', value=access, httponly=True, samesite='lax')
    response.set_cookie(key='refresh_token', value=refresh, httponly=True, samesite='lax')

    return {"access_token": access, "token_type": "bearer"}



@router.get("/me", response_model=schemas.UserOut)
def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=401, detail="No active session")

    payload = verify_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_id = payload.get("sub")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user



@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token_endpoint(response: Response, refresh_token: str = Cookie(None), 
                           db: Session = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    token_entry = crud.get_refresh_token(db, refresh_token)
    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = crud.get_user_by_id(db, token_entry.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token(str(user.id))
    response.set_cookie("access_token", new_access_token, httponly=True, samesite="lax")
    return {"access_token": new_access_token, "token_type": "bearer"}

# logout

