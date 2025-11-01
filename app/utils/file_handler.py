import os
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings


def save_profile_image(image: UploadFile, user_id: int) -> str:
    """
    프로필 이미지 저장
    
    Args:
        image: 업로드된 이미지 파일
        user_id: 사용자 ID
    
    Returns:
        저장된 이미지 경로 (상대 경로)
    """
    # 업로드 디렉토리 생성
    upload_dir = Path("uploads/profile")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 파일 확장자 추출
    ext = image.filename.split(".")[-1]
    
    # 고유 파일명 생성
    filename = f"{user_id}_{uuid.uuid4().hex}.{ext}"
    
    # 파일 저장
    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        f.write(image.file.read())
    
    # 상대 경로 반환
    return f"/uploads/profile/{filename}"


def delete_profile_image(image_path: str) -> None:
    """
    프로필 이미지 삭제
    
    Args:
        image_path: 이미지 경로
    """
    if not image_path:
        return
    
    # 절대 경로로 변환
    full_path = Path(image_path.lstrip("/"))
    
    if full_path.exists():
        full_path.unlink()