import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .auth import get_current_user
from .. import crud, schemas

router = APIRouter(prefix="/files", tags=["Files"])


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
CONTENT_TYPES = {"image/jpeg", "image/png"}
BASE_UPLOAD_DIR = "uploads/images"
CATEGORIES = {"matematik", "fizik", "kimya"}


for category in CATEGORIES:
    os.makedirs(os.path.join(BASE_UPLOAD_DIR, category), exist_ok=True)


@router.post("/upload", response_model=schemas.ImageResponse)
def upload_image(
    category: str = Query(..., description="matematik | fizik | kimya"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")

    extension = file.filename.split('.')[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if file.content_type not in CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid MIME type")

    file_id = uuid4()
    filename = f"{file_id}.{extension}"
    save_path = os.path.join(BASE_UPLOAD_DIR, category, filename)

    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    image = crud.create_image(
        db=db,
        id=file_id,
        user_id=current_user.id,
        file_path=f"/{save_path}",  
        file_type=file.content_type,
        category=category
    )

    return image


@router.get("/myimages", response_model=list[schemas.ImageResponse])
def get_my_images(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if category:
        return crud.get_images_for_user_by_category(db, current_user.id, category)

    return crud.get_images_for_user(db, current_user.id)
