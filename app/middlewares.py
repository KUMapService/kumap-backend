from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import APP_DIR


def setup_middlewares(app):
    """FastAPI 앱에 미들웨어 등록하는 함수"""

    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:51203",
        "https://landprice.info",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount(
        "/static", StaticFiles(directory=os.path.join(APP_DIR, "static")), name="static"
    )
