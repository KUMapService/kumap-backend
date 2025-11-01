from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_token

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_db() -> Generator:
    """데이터베이스 세션"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """현재 사용자 정보"""
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return payload

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[dict]:
    """
    현재 사용자 정보 (선택적 인증)
    
    토큰이 없으면 None 반환, 있으면 검증 후 payload 반환
    유효하지 않은 토큰이면 None 반환 (에러 발생 안 함)
    
    Returns:
        사용자 정보 dict or None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_token(token)
    
    return payload  # 유효하지 않으면 None, 유효하면 payload
