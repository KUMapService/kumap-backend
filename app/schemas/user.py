
from pydantic import BaseModel, EmailStr, Field

from app.schemas.land import LandData


# REQUEST DATA
class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="이메일")

class ChangeUserPasswordRequest(BaseModel):
    current_password: str = Field(..., description="현재 비밀번호")
    change_password: str = Field(..., description="변경할 비밀번호")

class ChangeLandLikeRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")


# RESPONSE DATA
class ChangeLandLikeResponse(BaseModel):
    like: bool = Field(..., description="해당 토지의 좋아요 여부")

class FavoriteLands(BaseModel):
    favorites: list[LandData] = Field(..., description="좋아요 한 토지 목록")
