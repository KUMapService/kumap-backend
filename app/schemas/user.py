from pydantic import Field, BaseModel, EmailStr


# REQUEST DATA
class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ChangeUserPasswordRequest(BaseModel):
    current_password: str
    change_password: str

class ChangeLandLikeRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")


# RESPONSE DATA
class ChangeLandLikeResponse(BaseModel):
    like: bool = Field(..., description="해당 토지의 좋아요 여부")

class GetFavoriteLandsByUserResponse(BaseModel):
    favorites: list = Field(..., description="좋아요 한 토지 목록")
