from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, files, quotes
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title='NOTOLOGY')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.mount(
    "/uploads", 
    StaticFiles(directory=str(settings.UPLOAD_BASE_DIR)), 
    name="uploads"
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(quotes.router)
