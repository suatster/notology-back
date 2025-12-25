import os
import re
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import uuid4
from ..database import get_db
from .auth import get_current_user
from .. import schemas
from app.core.config import settings

router = APIRouter(prefix="/files", tags=["Files"])

# Ensure base image directory exists; per-user and per-lesson dirs are
# created on-demand when a user uploads an image.
os.makedirs(settings.UPLOAD_IMAGE_DIR, exist_ok=True)


@router.post("/upload")
def upload_image(
    lesson: str = Query(..., description="Ders adı"), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    
    extension = file.filename.split('.')[-1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")


    if file.content_type not in settings.CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid MIME type")

   
    file_id = uuid4()
    filename = f"{file_id}.{extension}"

    username = getattr(current_user, "username", None)
    if not username:
        raise HTTPException(status_code=400, detail="Missing username in token payload")

    user_dir = os.path.join(settings.UPLOAD_IMAGE_DIR, username)

    lesson_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', lesson)

    lesson_dir = os.path.join(user_dir, lesson_safe)
    os.makedirs(lesson_dir, exist_ok=True)

    save_path = os.path.join(lesson_dir, filename)

    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    return {"message": "successful"}


@router.get("/myimages")
def get_my_images(
    lesson: str | None = Query(None, description="İsteğe bağlı ders adı"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    username = getattr(current_user, "username", None)
    if not username:
        raise HTTPException(status_code=400, detail="Missing username in token payload")

    user_dir = os.path.join(settings.UPLOAD_IMAGE_DIR, username)
    if not os.path.exists(user_dir):
        return {"images": []}

    images_list = []

    # Eğer lesson parametresi verilmişse sadece o klasörü kontrol et
    lesson_dirs = [lesson] if lesson else os.listdir(user_dir)

    for lesson_name in lesson_dirs:
        # Güvenli klasör ismi
        lesson_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', lesson_name)
        lesson_path = os.path.join(user_dir, lesson_safe)
        if os.path.isdir(lesson_path):
            for filename in os.listdir(lesson_path):
                file_path = os.path.join(lesson_path, filename)
                if os.path.isfile(file_path):
                    # Klasör yapısı ile path
                    images_list.append({
                        "lesson": lesson_safe,
                        "filename": filename,
                        "path": f"/uploads/images/{username}/{lesson_safe}/{filename}"
                    })

    return {"images": images_list}



@router.get("/image")
def get_image(
    path: str = Query(..., description="Dönmek istediğiniz resmin path’i"),
    current_user: dict = Depends(get_current_user)
):
    username = getattr(current_user, "username", None)
    if not username:
        raise HTTPException(status_code=400, detail="Missing username in token payload")
    path = path.lstrip("/")
    print(path)
    safe_path = os.path.normpath(path).replace("..", "")
    print(safe_path)
    file_path = safe_path.replace('/', '\\')
    print(file_path)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
