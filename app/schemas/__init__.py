from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

from app.enums.response import Status

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """표준 API 응답 포맷"""
    status: Status
    message: str = ""
    data: Optional[T] = None
    
    class Config:
        use_enum_values = True  # Enum을 값으로 직렬화


class MessageResponse(BaseModel):
    """단순 메시지 응답"""
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답"""
    items: list[T]
    total: int
    limit: int
    offset: int
    
    @property
    def has_more(self) -> bool:
        return self.offset + self.limit < self.total


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """에러 응답"""
    status: Status = Status.ERROR
    message: str
    errors: Optional[list[ErrorDetail]] = None


# 편의를 위한 export
__all__ = [
    "APIResponse",
    "MessageResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "ErrorDetail",
]