from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# REQUEST DATA
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="로그인할 이메일 주소", example="user@example.com")
    password: str = Field(..., description="로그인할 비밀번호", example="yourpassword123")


class DuplicateCheckRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, description="중복 확인할 이메일 주소", example="user@example.com")
    nickname: Optional[str] = Field(None, description="중복 확인할 닉네임", example="coolnickname")


class RegisterRequest(BaseModel):
    name: str = Field(..., description="사용자 이름", example="홍길동")
    nickname: str = Field(..., description="사용자 닉네임", example="hong123")
    email: EmailStr = Field(..., description="회원가입할 이메일 주소", example="user@example.com")
    password: str = Field(..., description="회원가입할 비밀번호", example="strongpassword!@#")


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="비밀번호 재설정할 이메일 주소", example="user@example.com")


# RESPONSE DATA
class LoginData(BaseModel):
    access_token: str = Field(..., description="발급된 액세스 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="발급된 리프레시 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")


class ProtectedUserData(BaseModel):
    email: EmailStr = Field(..., description="사용자 이메일", example="user@example.com")
    name: str = Field(..., description="사용자 이름", example="홍길동")
    nickname: str = Field(..., description="사용자 닉네임", example="hong123")
    phone: str = Field(..., description="사용자 전화번호", example="010-1234-5678")
    phone_verified: bool = Field(..., description="전화번호 인증 여부", example=True)
    image: str = Field(..., description="프로필 이미지 URL", example="https://api.landprice.info/static/images/default-user-image.png")


class RefreshTokenData(BaseModel):
    access_token: str = Field(..., description="새로 발급된 액세스 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
