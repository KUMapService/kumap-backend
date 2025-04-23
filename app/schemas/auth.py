from pydantic import BaseModel, EmailStr
from typing import Optional


# REQUEST DATA
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class DuplicateCheckRequest(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None

class RegisterRequest(BaseModel):
    name: str
    nickname: str
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr


# RESPONSE DATA
class LoginData(BaseModel):
    access_token: str
    refresh_token: str

class ProtectedUserData(BaseModel):
    email: EmailStr
    name: str
    nickname: str
    phone: str
    phone_verified: bool
    image: str

class RefreshTokenData(BaseModel):
    access_token: str
