
from pydantic import BaseModel, EmailStr, Field

from app.dto.land_dto import LandDetailDTO


# REQUEST DATA
class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="이메일")


class UpdateProfileRequest(BaseModel):
    """프로필 수정 요청"""
    name: str = Field(..., min_length=1, max_length=50)
    nickname: str = Field(..., min_length=1, max_length=20)
    phone: str = Field(..., pattern=r"^01\d{8,9}$")


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    
    def validate_passwords_different(self):
        """새 비밀번호가 현재 비밀번호와 다른지 확인"""
        if self.current_password == self.new_password:
            raise ValueError("새 비밀번호는 현재 비밀번호와 달라야 합니다.")


# RESPONSE DATA
class UserProfileResponse(BaseModel):
    """프로필 조회 응답 (API)"""
    email: EmailStr
    name: str
    nickname: str
    phone: str
    phone_verified: bool
    profile_image_url: str


class ChangeLandLikeResponse(BaseModel):
    like: bool = Field(..., description="해당 토지의 좋아요 여부")

class FavoriteLands(BaseModel):
    favorites: list[LandDetailDTO] = Field(..., description="좋아요 한 토지 목록")

class MyLandsResponse(BaseModel):
    lands: list[LandDetailDTO] = Field(..., description="내 소유 토지 목록")

class MyListingsResponse(BaseModel):
    listings: list[LandDetailDTO] = Field(..., description="내가 등록한 매물 목록")
