from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exception_handlers import http_exception_handler, validation_exception_handler
from app.middlewares import setup_middlewares
from app.routes import setup_routers
from app.schemas import APIResponse, error


# FastAPI 앱 생성
app = FastAPI(
    title="KUMap API 문서",
    description="KUMap 토지가치예측서비스 백엔드 API 문서입니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 에러 핸들러 등록
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 미들웨어 등록
setup_middlewares(app)

# 라우터 등록
setup_routers(app)

# 서버 상태 체크
@app.get(
    "/", 
    response_model=APIResponse, 
    responses=error.make_error_responses(need_422=False, need_500=True),
    summary="서버 상태 확인", 
    description="서버가 정상적으로 동작하고 있는지 상태를 확인하는 엔드포인트입니다."
)
def server_status():
    return APIResponse(
        status="success",
        message="서버가 정상적으로 동작하고 있습니다.",
    )
