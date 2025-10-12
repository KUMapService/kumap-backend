from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    비밀번호 해싱
    
    Args:
        password: 평문 비밀번호
    
    Returns:
        해싱된 비밀번호
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해싱된 비밀번호
    
    Returns:
        비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Access Token 생성
    
    Args:
        data: 토큰에 담을 데이터 (예: {"sub": "user@example.com"})
        expires_delta: 만료 시간 (기본: settings에서 가져옴)
    
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Refresh Token 생성
    
    Args:
        data: 토큰에 담을 데이터
    
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 디코딩 및 검증
    
    Args:
        token: JWT 토큰 문자열
    
    Returns:
        토큰 payload 또는 None (유효하지 않은 경우)
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    토큰 검증 (타입 확인 포함)
    
    Args:
        token: JWT 토큰
        token_type: "access" 또는 "refresh"
    
    Returns:
        payload 또는 None
    """
    payload = decode_token(token)
    
    if not payload:
        return None
    
    # 토큰 타입 확인
    if payload.get("type") != token_type:
        return None
    
    # 만료 시간 확인 (jwt.decode에서 자동으로 체크되지만 명시적으로)
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
        return None
    
    return payload


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Refresh Token으로 새 Access Token 발급
    
    Args:
        refresh_token: Refresh Token
    
    Returns:
        새로운 Access Token 또는 None
    """
    payload = verify_token(refresh_token, token_type="refresh")
    
    if not payload:
        return None
    
    # 새 Access Token 생성
    new_access_token = create_access_token(
        data={"sub": payload.get("sub")}
    )
    
    return new_access_token
