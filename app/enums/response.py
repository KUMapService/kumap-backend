from enum import Enum


class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAIL = "fail"
    UNAUTHORIZED = "unauthorized"
