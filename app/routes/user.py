
from fastapi import APIRouter, Depends, File, Form, UploadFile
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.security import JWTBearer
from app.db.session import get_db
from app.enums.response import Status
from app.schemas import APIResponse, user
from app.schemas.land import LandData
from app.services.user import user_service

user_router = APIRouter(prefix="/user")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user_router.post(
    "/reset-password",
    response_model=APIResponse,
    summary="비밀번호 초기화",
    description="이메일을 기반으로 임시 비밀번호를 생성하고, 해당 이메일로 메일을 발송합니다."
)
async def reset_password(request: user.ResetPasswordRequest, db: Session = Depends(get_db)):
    return user_service.reset_password(request, db)


@user_router.get(
    "/images/{file_name}",
    summary="사용자 프로필 이미지 조회",
    description="파일명이 주어지면 해당 이미지를 반환하고, 없으면 기본 이미지를 반환합니다."
)
@user_router.get(
    "/images",
    include_in_schema=False  # 중복 등록 방지
)
async def get_user_image(file_name: str | None = None):
    return user_service.get_user_image(file_name)


@user_router.post(
    "/modify-user-info",
    response_model=APIResponse,
    summary="사용자 정보 수정",
    description="사용자 이름, 닉네임, 전화번호, 프로필 이미지를 수정합니다. FormData 형식으로 요청합니다."
)
async def modify_user_info(
    name: str = Form(...),
    nickname: str = Form(...),
    phone: str = Form(...),
    is_image_deleted: bool = Form(False),
    image: UploadFile | None = File(None),
    payload: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    user_service.modify_user_info(name, nickname, phone, is_image_deleted, image, payload, db)
    return APIResponse(
        status=Status.SUCCESS,
        message="사용자 정보를 성공적으로 변경했습니다.",
    )


@user_router.post(
    "/change-password",
    response_model=APIResponse,
    summary="비밀번호 변경",
    description="현재 비밀번호를 검증한 후, 새로운 비밀번호로 변경합니다."
)
async def change_password(
    request: user.ChangeUserPasswordRequest,
    payload: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    user_service.change_password(request.current_password, request.change_password, payload, db)
    return APIResponse(
        status=Status.SUCCESS,
        message="비밀번호가 변경되었습니다.",
    )


@user_router.post(
    "/change-land-like",
    response_model=APIResponse,
    summary="토지 좋아요 토글",
    description="현재 토지가 사용자의 즐겨찾기에 등록되어 있으면 제거하고, 없으면 추가합니다."
)
def patch_land_like_status(
    request: user.ChangeLandLikeRequest,
    payload: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    if user_service.toggle_favorite(request.pnu, payload, db):
        return APIResponse(
            status=Status.SUCCESS,
            message="관심있는 토지로 등록이 완료되었습니다.",
            data=True,
        )
    else:
        return APIResponse(
            status=Status.SUCCESS,
            message="관심있는 토지에서 등록이 해제되었습니다.",
            data=False,
        )

@user_router.get(
    "/get-favorite-lands-by-user",
    response_model=APIResponse[list[LandData]],
    summary="사용자의 즐겨찾기 토지 목록 조회",
    description="로그인한 사용자가 좋아요한 토지 목록을 반환합니다."
)
def get_favorite_land(payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)):
    data = user_service.get_favorite_lands(payload, db)
    return APIResponse[list[LandData]](
        status=Status.SUCCESS,
        message="나의 토지 관심 목록을 불러왔습니다.",
        data=data,
    )

@user_router.get(
    "/get-listings",
    response_model=APIResponse[list[LandData]],
    summary="사용자의 즐겨찾기 토지 목록 조회",
    description="로그인한 사용자가 좋아요한 토지 목록을 반환합니다."
)
def get_listings(payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)):
    data = user_service.get_listings(payload, db)
    return APIResponse[list[LandData]](
        status=Status.SUCCESS,
        message="나의 토지 관심 목록을 불러왔습니다.",
        data=data,
    )
