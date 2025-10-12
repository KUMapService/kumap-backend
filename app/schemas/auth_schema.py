from pydantic import BaseModel, EmailStr, Field


# REQUEST DATA
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="로그인할 이메일 주소", example="user@example.com")
    password: str = Field(..., description="로그인할 비밀번호", example="yourpassword123")


class SignUpRequest(BaseModel):
    name: str = Field(..., description="사용자 이름", example="홍길동")
    nickname: str = Field(..., description="사용자 닉네임", example="hong123")
    email: EmailStr = Field(..., description="회원가입할 이메일 주소", example="user@example.com")
    password: str = Field(..., description="회원가입할 비밀번호", example="strongpassword!@#")


class DuplicateCheckRequest(BaseModel):
    email: EmailStr | None = Field(None, description="중복 확인할 이메일 주소", example="user@example.com")
    nickname: str | None = Field(None, description="중복 확인할 닉네임", example="coolnickname")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="리프레시 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")


# RESPONSE DATA
class TokenResponse(BaseModel):
    access_token: str = Field(..., description="발급된 액세스 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="발급된 리프레시 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

