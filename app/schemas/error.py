
from fastapi import status
from pydantic import BaseModel, Field

from app.enums.response import Status


class BadRequestResponse(BaseModel):
    status: Status = Field(Status.FAIL, example="fail")
    message: str = Field(..., example="요청이 잘못되었습니다.")

class UnauthorizedResponse(BaseModel):
    status: Status = Field(Status.UNAUTHORIZED, example="unauthorized")
    message: str = Field(..., example="인증에 실패했습니다.")

class ForbiddenResponse(BaseModel):
    status: Status = Field(Status.UNAUTHORIZED, example="unauthorized")
    message: str = Field(..., example="접근 권한이 없습니다.")

class NotFoundResponse(BaseModel):
    status: Status = Field(Status.FAIL, example="fail")
    message: str = Field(..., example="요청한 리소스를 찾을 수 없습니다.")

class ConflictResponse(BaseModel):
    status: Status = Field(Status.FAIL, example="fail")
    message: str = Field(..., example="이미 존재하는 리소스입니다.")

class ValidationFailResponse(BaseModel):
    status: Status = Field(Status.FAIL, example="fail")
    message: str = Field(..., example="요청 데이터가 올바르지 않습니다.")

class InternalServerErrorResponse(BaseModel):
    status: Status = Field(Status.ERROR, example="error")
    message: str = Field(..., example="서버 오류가 발생했습니다.")


def make_error_responses(
    need_400: bool = False,
    need_401: bool = False,
    need_403: bool = False,
    need_404: bool = False,
    need_409: bool = False,
    need_422: bool = True,
    need_500: bool = True,
) -> dict[int, dict]:
    """Swagger 문서에 에러 코드 정의를 위한 에러 응답 생성 함수.
    """
    responses = {}
    if need_400:
        responses[status.HTTP_400_BAD_REQUEST] = {"model": BadRequestResponse}
    if need_401:
        responses[status.HTTP_401_UNAUTHORIZED] = {"model": UnauthorizedResponse}
    if need_403:
        responses[status.HTTP_403_FORBIDDEN] = {"model": ForbiddenResponse}
    if need_404:
        responses[status.HTTP_404_NOT_FOUND] = {"model": NotFoundResponse}
    if need_409:
        responses[status.HTTP_409_CONFLICT] = {"model": ConflictResponse}
    if need_422:
        responses[status.HTTP_422_UNPROCESSABLE_ENTITY] = {"model": ValidationFailResponse}
    if need_500:
        responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = {"model": InternalServerErrorResponse}
    return responses
