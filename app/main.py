from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exception_handlers import (
    http_exception_handler,
    validation_exception_handler
)
from app.middlewares import setup_middlewares
from app.api.v1.routes import api_router as v1_router

# FastAPI 앱 생성
app = FastAPI(
    title="KUMap API",
    description="토지가치예측서비스 백엔드 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 예외 핸들러 등록
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 미들웨어 등록
setup_middlewares(app)

# API 라우터 등록
app.include_router(v1_router, prefix="/api/v1")


# 헬스체크 (버전 없음)
@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "version": "1.0.0"
    }


@app.get("/")
def root():
    """API 루트"""
    return {
        "message": "KUMap API",
        "version": "1.0.0",
        "docs": "/docs"
    }