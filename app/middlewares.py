from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings


def setup_middlewares(app: FastAPI):
    """FastAPI 앱에 미들웨어 등록"""
    
    # CORS 설정을 config에서 가져오기
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Static files
    app.mount(
        "/static",
        StaticFiles(directory=settings.upload_dir.parent),
        name="static"
    )
