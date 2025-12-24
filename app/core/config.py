from pydantic_settings import BaseSettings
from typing import Set

class Settings(BaseSettings):
    
    DATABASE_URL: str
    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str = "HS256"
    FRONTEND_ORIGIN: str
    UPLOAD_BASE_DIR: str = "uploads"
    UPLOAD_IMAGE_DIR: str = "uploads/images"
    ALLOWED_EXTENSIONS: Set[str] = {"jpg", "jpeg", "png"}
    CONTENT_TYPES: Set[str] = {"image/jpeg", "image/png"}
    LESSONS: Set[str] = {"mathematic", "physic", "chemistry"} 
    QUOTABLE_RANDOM_URL: str = "https://api.quotable.io/random"
    MAX_CACHE_SIZE: int = 10
    MAX_RETRY: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
