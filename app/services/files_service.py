import os
import re
from uuid import uuid4
from fastapi import UploadFile, Depends
from .. import schemas
from ..core.config import settings
from ..dependencies.auth_dependency import get_current_user

class FileServiceException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class FilesService:
    
    def __init__(self, upload_dir: str = settings.UPLOAD_IMAGE_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)


    def save_lesson_file(self, lesson: str, file: UploadFile, current_user: schemas.User) -> str:
        extension = file.filename.split('.')[-1].lower()
        if extension not in settings.ALLOWED_EXTENSIONS:
            raise FileServiceException("Invalid file type")

        if file.content_type not in settings.CONTENT_TYPES:
            raise FileServiceException("Invalid MIME type")

        username = getattr(current_user, "username", None)
        if not username:
            raise FileServiceException("Missing username in user object")

        user_dir = os.path.join(self.upload_dir, username)
        lesson_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', lesson)
        lesson_dir = os.path.join(user_dir, lesson_safe)
        os.makedirs(lesson_dir, exist_ok=True)

        file_id = uuid4()
        filename = f"{file_id}.{extension}"
        save_path = os.path.join(lesson_dir, filename)

        try:
            with open(save_path, "wb") as buffer:
                buffer.write(file.file.read())
        except Exception as e:
            raise FileServiceException(f"Failed to save file: {str(e)}")

        return save_path



    def get_user_images(self, current_user: schemas.User, lesson: str | None = None) -> list[dict]:
        username = getattr(current_user, "username", None)
        if not username:
            raise FileServiceException("Missing username in user object")

        user_dir = os.path.join(self.upload_dir, username)
        if not os.path.exists(user_dir):
            return []

        images_list = []

        lesson_dirs = [lesson] if lesson else os.listdir(user_dir)

        for lesson_name in lesson_dirs:
            lesson_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', lesson_name)
            lesson_path = os.path.join(user_dir, lesson_safe)
            if os.path.isdir(lesson_path):
                for filename in os.listdir(lesson_path):
                    file_path = os.path.join(lesson_path, filename)
                    if os.path.isfile(file_path):
                        images_list.append({
                            "lesson": lesson_safe,
                            "filename": filename,
                            "path": f"/uploads/images/{username}/{lesson_safe}/{filename}"
                        })

        return images_list
    


    def delete_file(self, current_user: schemas.User, path: str) -> None:
        username = getattr(current_user, "username", None)
        if not username:
            raise FileServiceException("Missing username in token payload")
        
        cwd = os.getcwd()
        file_path = os.path.abspath(os.path.join(cwd, path.lstrip("/").replace("/", os.sep)))

        if username not in file_path:
            raise FileServiceException("Unauthorized file path")
        
        if not os.path.isfile(file_path):
            raise FileServiceException("File not found")

        os.remove(file_path)
