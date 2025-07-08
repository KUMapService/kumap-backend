from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JWTBearer:
    def __init__(self, auto_error: bool = True):
        self.auto_error = auto_error

    def __call__(self, request: Request):
        token = request.headers.get("Authorization")
        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization token missing",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        try:
            token = token.split(" ")[1]
            payload = self.decode_jwt(token)
            return payload
        except JWTError:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

    def decode_jwt(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """엑세스 토큰 생성 함수."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """리프레시 토큰 생성 함수."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)   # 보통 리프레시 토큰은 7일짜리
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
