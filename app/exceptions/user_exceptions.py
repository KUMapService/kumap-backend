# exceptions/user_exceptions.py
"""
사용자 관련 예외
"""
from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    """사용자를 찾을 수 없음"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )


class InvalidPasswordException(HTTPException):
    """비밀번호 불일치"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 일치하지 않습니다."
        )


class DuplicateEmailException(HTTPException):
    """이메일 중복"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다."
        )


class DuplicateNicknameException(HTTPException):
    """닉네임 중복"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 닉네임입니다."
        )