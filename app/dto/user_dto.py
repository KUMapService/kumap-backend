from pydantic import BaseModel, EmailStr, Field


class UserProfileDTO(BaseModel):
    """사용자 프로필 DTO"""
    email: EmailStr
    name: str
    nickname: str
    phone: str = ""
    phone_verified: bool = False
    profile_image_url: str
    
    class Config:
        from_attributes = True

