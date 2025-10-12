from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.enums.response import Status
from app.schemas import APIResponse, error
from app.schemas.auth_schema import (
    LoginRequest,
    DuplicateCheckRequest,
    SignUpRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(user_repo=UserRepository(db))


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="로그인",
    description="이메일과 비밀번호를 통해 로그인하고 Access/Refresh 토큰을 발급받습니다."
)
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    tokens = auth_service.login(request.email, request.password)
    return APIResponse[TokenResponse](
        status=Status.SUCCESS,
        message="로그인에 성공하였습니다.",
        data=TokenResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token
        ),
    )


@router.post(
    "/signup",
    response_model=APIResponse,
    summary="회원가입",
    description="이름, 이메일, 비밀번호, 닉네임을 통해 회원가입을 진행합니다."
)
def signup(request: SignUpRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.signup(
        name=request.name,
        email=request.email,
        password=request.password,
        nickname=request.nickname,
    )
    return APIResponse(
        status=Status.SUCCESS,
        message="회원가입을 완료하였습니다.",
    )


@router.post(
    "/check",
    response_model=APIResponse,
    responses=error.make_error_responses(need_409=True),
    summary="이메일/닉네임 중복 체크",
    description="이메일 또는 닉네임의 중복 여부를 확인합니다."
)
def duplicate_check(request: DuplicateCheckRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.check_duplicate(
        email=request.email,
        nickname=request.nickname
    )
    return APIResponse(
        status=Status.SUCCESS,
        message="사용 가능합니다."
    )


@router.post(
    "/refresh", 
    response_model=APIResponse[TokenResponse],
    summary="토큰 갱신",
    description="Refresh 토큰을 통해 Access 토큰을 갱신합니다."
)
def refresh_token(request: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    """토큰 갱신"""
    access_token = auth_service.refresh_access_token(request.refresh_token)
    return APIResponse[TokenResponse](
        status=Status.SUCCESS,
        message="토큰 갱신에 성공하였습니다.",
        data=TokenResponse(
            access_token=access_token
        ),
    )
