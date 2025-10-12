from datetime import timedelta
from fastapi import HTTPException, status
from typing import Optional

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password
)
from app.dto.auth_dto import TokenDTO, DuplicateCheckDTO
from app.models.user_model import User
from app.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    NicknameAlreadyExistsException
)
from app.repositories.user_repository import UserRepository


class AuthService:
    """인증(Authentication) 서비스"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, email: str, password: str) -> TokenDTO:
        """
        사용자가 입력한 이메일과 비밀번호를 검증하고,
        Access/Refresh 토큰을 발급한다.
        """
        user = self.user_repo.find_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 잘못되었습니다."
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            {"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token({"sub": user.email})

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)

    def signup(self, name: str, email: str, password: str, nickname: str) -> None:
        """
        사용자 회원가입 처리
        """
        # TODO: 유효성 검증 로직 추가
        
        # 중복 체크
        if self.user_repo.exists_by_email(email):
            raise EmailAlreadyExistsException()
        
        if self.user_repo.exists_by_nickname(nickname):
            raise NicknameAlreadyExistsException()
        
        # 사용자 생성
        new_user = User(
            email=email,
            password=hash_password(password),
            name=name,
            nickname=nickname,
        )
        self.user_repo.create(new_user)

    def check_duplicate(
        self,
        email: Optional[str],
        nickname: Optional[str]
    ) -> DuplicateCheckDTO:
        """
        이메일 또는 닉네임 중복 확인.
        """
        if self.user_repo.exists_by_email(email):
            raise EmailAlreadyExistsException()
        
        if self.user_repo.exists_by_nickname(nickname):
            raise NicknameAlreadyExistsException()
        