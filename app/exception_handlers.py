from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.enums.response import Status


def get_status_from_code(code: int) -> Status:
    if 200 <= code < 300:
        return Status.SUCCESS
    if code == 401:
        return Status.UNAUTHORIZED
    if 400 <= code < 500:
        return Status.FAIL
    if 500 <= code < 600:
        return Status.ERROR
    return Status.ERROR

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": get_status_from_code(exc.status_code),
            "message": str(exc.detail),
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": Status.FAIL,
            "message": "요청 데이터가 유효하지 않습니다.",
        },
    )
