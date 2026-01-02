from fastapi import APIRouter,HTTPException, Response, Depends, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas
from ..core.config import settings
from ..database import get_db
from ..dependencies.auth_dependency import get_current_user
from ..services.auth_service import (
    AuthService,
    UserAlreadyExists,
    MissingRefreshToken,
    InvalidOrExpiredRefreshToken,
)



router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/register", response_model=schemas.RegisterResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        user = service.register(
            payload.username,
            payload.email,
            payload.password
        )
    except UserAlreadyExists as e:
        raise HTTPException(status_code=400, detail={"message": str(e)})

    return schemas.RegisterResponse(
        message="You successfully registered",
        user=user
    )



@router.post("/login")
def token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    result = service.login(form_data.username, form_data.password)

    if not result:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    response.set_cookie(
        key="access_token", 
        value=result["access"], 
        httponly=True, 
        samesite="none",
        secure=False, 
        path="/", 
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 60
    )

    response.set_cookie(
        key="refresh_token", 
        value=result["refresh"],
        httponly=True, 
        samesite="none",
        secure=False, 
        path="/", 
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
   
    return {"message": "Login successful"}



@router.get("/me", response_model=schemas.User)
def me(current_user=Depends(get_current_user)):
    return current_user



@router.post("/refresh")
def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        tokens = auth_service.refresh_tokens(refresh_token)
    except MissingRefreshToken as e:
        raise HTTPException(status_code=401, detail={"message": str(e)})
    except InvalidOrExpiredRefreshToken as e:
        raise HTTPException(status_code=401, detail={"message": str(e)})

    response.set_cookie(
        key="access_token", 
        value=tokens["access"], 
        httponly=True, 
        samesite="none", 
        secure=False, 
        path="/", 
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 60
    )

    response.set_cookie(
        key="refresh_token", 
        value=tokens["refresh"], 
        httponly=True, 
        samesite="none", 
        secure=False, 
        path="/", 
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {"message": "Token refreshed"}



@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  
):
    service = AuthService(db)
    service.logout_user(current_user.id)

    response.delete_cookie("access_token", path="/", samesite="none", secure=False)
    response.delete_cookie("refresh_token", path="/", samesite="none", secure=False)

    return {"message": "You successfully logged out"}
