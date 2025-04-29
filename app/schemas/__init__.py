from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

from app.enums.response import Status

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    status: Status
    message: str
    data: Optional[T] = None
