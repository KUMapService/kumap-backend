from fastapi import APIRouter, Depends, File, Form, UploadFile
from typing import List
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.enums.response import Status
from app.schemas import APIResponse
from app.schemas.user_schema import MyLandsResponse, MyListingsResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserProfileResponse, ChangePasswordRequest

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """UserService 의존성 주입"""
    return UserService(user_repo=UserRepository(db))


@router.get("/me", response_model=APIResponse[UserProfileResponse])
def get_my_profile(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """내 프로필 조회"""
    user = user_service.get_profile(current_user["sub"])
    return APIResponse[UserProfileResponse](
        status=Status.SUCCESS,
        message="내 프로필을 성공적으로 불러왔습니다.",
        data=UserProfileResponse(
            email=user.email,
            name=user.name,
            nickname=user.nickname,
            phone=user.phone,
            phone_verified=user.phone_verified,
            profile_image_url=user.profile_image_url,
        ),
    )


@router.put("/me")
def update_profile(
    name: str = Form(...),
    nickname: str = Form(...),
    phone: str = Form(...),
    is_image_deleted: bool = Form(False),
    image: UploadFile | None = File(None),
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """프로필 수정"""
    user_service.update_profile(
        email=current_user["sub"],
        name=name,
        nickname=nickname,
        phone=phone,
        is_image_deleted=is_image_deleted,
        image=image
    )
    return APIResponse(
        status=Status.SUCCESS,
        message="프로필이 수정되었습니다.",
    )

@router.put("/me/password")
def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """비밀번호 변경"""
    user_service.change_password(
        email=current_user["sub"],
        current_password=request.current_password,
        new_password=request.new_password
    )
    return APIResponse(
        status=Status.SUCCESS,
        message="비밀번호가 변경되었습니다.",
    )


@router.get("/me/lands")
def get_my_lands(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """내 소유 토지 목록"""
    owned_lands = user_service.get_owned_lands(current_user["sub"])
    return APIResponse[MyLandsResponse](
        status=Status.SUCCESS,
        message="내 소유 토지 목록을 성공적으로 불러왔습니다.",
        data=owned_lands,
    )


@router.get("/me/listings")
def get_my_listings(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """내가 등록한 매물 목록"""
    my_listings = user_service.get_my_listings(current_user["sub"])
    return APIResponse[MyListingsResponse](
        status=Status.SUCCESS,
        message="내가 등록한 매물 목록을 성공적으로 불러왔습니다.",
        data=my_listings,
    )