import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .auth import get_current_user
from .. import crud, schemas
from app.core.config import settings

router = APIRouter(prefix="/files", tags=["Files"])


for lesson in settings.LESSONS:
    os.makedirs(os.path.join(settings.UPLOAD_IMAGE_DIR, lesson), exist_ok=True)


@router.post("/upload", response_model=schemas.ImageResponse)
def upload_image(
    lesson: str = Query(..., description="mathematic | physic | chemistry"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if lesson not in settings.LESSONS:
        raise HTTPException(status_code=400, detail="Invalid lesson choosing.")

    extension = file.filename.split('.')[-1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if file.content_type not in settings.CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid MIME type")

    file_id = uuid4()
    filename = f"{file_id}.{extension}"
    save_path = os.path.join(settings.UPLOAD_IMAGE_DIR, lesson, filename)

    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    image = crud.create_image(
        db=db,
        id=file_id,
        user_id=current_user.id,
        file_path=f"/{save_path}",  
        file_type=file.content_type,
        lesson=lesson
    )

    return image


@router.get("/myimages", response_model=list[schemas.ImageResponse])
def get_my_images(
    lesson: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if lesson:
        return crud.get_images_for_user_by_lesson(db, current_user.id, lesson)

    return crud.get_images_for_user(db, current_user.id)
