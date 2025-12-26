
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
import os
from .. import schemas
from .auth import get_current_user
from ..core.config import settings
from ..services.files_service import FilesService, FileServiceException


router = APIRouter(prefix="/files", tags=["Files"])

os.makedirs(settings.UPLOAD_IMAGE_DIR, exist_ok=True)

files_service = FilesService()


@router.post("/upload")
def upload_image(
    lesson: str = Query(..., description="lesson"),
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(get_current_user)
):
    try:
        files_service.save_lesson_file(lesson, file, current_user)
    except FileServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)

    return {"message": "File uploaded successfully"}



@router.get("/myimages")
def get_my_images(
    lesson: str | None = Query(None, description="lesson"),
    current_user: schemas.User = Depends(get_current_user)
):
    try:
        images = files_service.get_user_images(current_user, lesson)
    except FileServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)

    return {"images": images}



@router.get("/image/get")
def get_image(
    path: str = Query(..., description="path"),
    current_user: dict = Depends(get_current_user)
):
    username = getattr(current_user, "username", None)
    if not username:
        raise HTTPException(status_code=400, detail="Missing username in token payload")
    path = path.lstrip("/")
    safe_path = os.path.normpath(path).replace("..", "")
    file_path = safe_path.replace('/', '\\')
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)



@router.delete("/image/delete")
def delete_image(
    path: str = Query(..., description="path"),
    current_user: schemas.User = Depends(get_current_user)
):
    try:
        files_service.delete_file(current_user, path)
    except FileServiceException as e:
        raise HTTPException(status_code=400, detail=e.message)

    return {"message": "File deleted successfully"}
