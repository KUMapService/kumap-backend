from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import SERVER_DOMAIN
from app.core.security import JWTBearer
from app.db.session import get_db
from app.enums.response import Status
from app.models.user import User
from app.schemas import APIResponse, error, auth
from app.services.auth import auth_service

auth_router = APIRouter(prefix="/auth")


@auth_router.post(
    "/login", 
    response_model=APIResponse[auth.LoginData], 
    responses=error.make_error_responses(need_401=True),
    summary="로그인", 
    description="이메일과 비밀번호를 통해 로그인하고 Access/Refresh 토큰을 발급받습니다."
)
async def login(request: auth.LoginRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = auth_service.login(request, db)
    return APIResponse[auth.LoginData](
        status=Status.SUCCESS,
        message="로그인에 성공하였습니다.",
        data=auth.LoginData(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )

@auth_router.post(
    "/dup-check", 
    response_model=APIResponse,
    responses=error.make_error_responses(need_409=True),
    summary="중복 체크", 
    description="이메일 또는 닉네임의 중복 여부를 확인합니다."
)
async def duplicate_check(request: auth.DuplicateCheckRequest, db: Session = Depends(get_db)):
    auth_service.duplicate_check(request, db)
    return APIResponse(
        status=Status.SUCCESS,
        message="사용 가능합니다.",
    )

@auth_router.post(
    "/sign-up", 
    response_model=APIResponse,
    responses=error.make_error_responses(need_409=True),
    summary="회원가입", 
    description="이름, 이메일, 비밀번호, 닉네임을 통해 회원가입을 진행합니다."
)
async def signup(request: auth.RegisterRequest, db: Session = Depends(get_db)):
    auth_service.signup(request, db)
    return APIResponse(
        status=Status.SUCCESS,
        message="회원가입을 완료하였습니다.",
    )

@auth_router.get(
    "/protected", 
    response_model=APIResponse[auth.ProtectedUserData],
    responses=error.make_error_responses(need_401=True, need_404=True),
    summary="보호된 라우트 인증", 
    description="JWT 토큰을 통해 사용자의 인증 상태를 확인합니다."
)
async def protected(payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)):
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    return APIResponse[auth.ProtectedUserData](
        status=Status.SUCCESS,
        message="사용자 인증에 성공하였습니다.",
        data=auth.ProtectedUserData(
            email=user.email,
            name=user.name,
            nickname=user.nickname,
            phone=user.phone if user.phone else "",
            phone_verified=user.phone_verified,
            image=SERVER_DOMAIN + (user.profile_image_url if user.profile_image_url else "/user/images"),
        ),
    )
