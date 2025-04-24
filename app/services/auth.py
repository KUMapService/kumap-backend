from datetime import timedelta
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils import auth
from app.core.security import create_access_token, create_refresh_token

ACCESS_TOKEN_EXPIRE_MINUTES = 300


class AuthService:
    """인증(Authentication) 관련 서비스 로직을 처리하는 클래스."""

    def login(self, request, db: Session) -> Tuple[str, str]:
        """
        사용자가 입력한 이메일과 비밀번호를 검증하고,
        Access/Refresh 토큰을 발급한다.
        """
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not auth.verify_password(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="아이디 또는 비밀번호가 잘못되었습니다."
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            {"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token({"sub": user.email})

        return access_token, refresh_token

    def signup(self, request, db: Session) -> None:
        """
        사용자 회원가입 처리.
        """
        try:
            auth.validate_signup_form(request.email, request.nickname, request.password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=409,
                detail="User already exists with this email"
            )

        if db.query(User).filter(User.nickname == request.nickname).first():
            raise HTTPException(
                status_code=409,
                detail="Duplicate nickname"
            )

        new_user = User(
            email=request.email,
            password=auth.get_password_hash(request.password),
            name=request.name,
            nickname=request.nickname,
        )
        db.add(new_user)
        db.commit()

    def duplicate_check(self, request, db: Session) -> None:
        """
        이메일 또는 닉네임 중복 확인.
        """
        if request.email and db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=409,
                detail="User already exists with this email"
            )

        if request.nickname and db.query(User).filter(User.nickname == request.nickname).first():
            raise HTTPException(
                status_code=409,
                detail="Duplicate nickname"
            )

auth_service = AuthService()
