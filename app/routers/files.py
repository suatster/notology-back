from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
import os
from ..database import get_db
from .auth import get_current_user
from .. import crud, schemas  


router = APIRouter(prefix="/files", tags=["Files"])


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
CONTENT_TYPES = {"image/jpeg", "image/png"}
UPLOAD_DIR = "uploads/images"


os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=schemas.ImageResponse)
def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)  # buradan user alıyoruz
):
    # Uzantı kontrolü
    extension = file.filename.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type!")

    # MIME türü kontrolü
    if file.content_type not in CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG or PNG allowed.")

    # Benzersiz dosya adı
    file_id = uuid4() 
    new_filename = f"{file_id}.{extension}"
    save_path = os.path.join(UPLOAD_DIR, new_filename)

    # Dosyayı kaydet
    with open(save_path, "wb") as buffer:
        buffer.write(file.file.read())

    db_image = crud.create_image(
        db=db,
        id=file_id,
        user_id=current_user.id,
        file_path=f"/{save_path}", 
        file_type=file.content_type
    )

    return db_image
