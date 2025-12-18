import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .database import engine, Base
from .routers import auth, files, quotes
from fastapi.staticfiles import StaticFiles

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title='NOTOLOGY')

origins = os.getenv('FRONTEND_ORIGIN', '*')
app.add_middleware(
CORSMiddleware,
allow_origins=[origins] if origins != '*' else ['*'],
allow_credentials=True,
allow_methods=['*'],
allow_headers=['*']
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(quotes.router)
