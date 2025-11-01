# api/v1/routes/favorite_routes.py
# 아직 검수 안끝남
"""
토지 좋아요 API
- 좋아요 추가/삭제
- 좋아요 목록 조회
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.services.favorite_service import FavoriteService
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.land_repository import LandRepository
from app.schemas.favorite_schema import FavoriteListResponse

router = APIRouter(prefix="/favorites", tags=["Favorites"])


def get_favorite_service(db: Session = Depends(get_db)) -> FavoriteService:
    """FavoriteService 의존성 주입"""
    return FavoriteService(
        favorite_repo=FavoriteRepository(db),
        land_repo=LandRepository(db)
    )


@router.post("/lands/{pnu}")
def add_favorite(
    pnu: str,
    current_user: dict = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    """
    토지 좋아요 추가
    
    - 이미 좋아요한 토지면 409 에러
    """
    favorite_service.add_favorite(pnu, current_user["sub"])
    return {"message": "관심 토지로 등록되었습니다."}


@router.delete("/lands/{pnu}")
def remove_favorite(
    pnu: str,
    current_user: dict = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    """토지 좋아요 취소"""
    favorite_service.remove_favorite(pnu, current_user["sub"])
    return {"message": "관심 토지에서 해제되었습니다."}


@router.post("/lands/{pnu}/toggle")
def toggle_favorite(
    pnu: str,
    current_user: dict = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    """
    토지 좋아요 토글
    
    - 있으면 삭제, 없으면 추가
    - 결과: {"is_liked": true/false}
    """
    is_liked = favorite_service.toggle_favorite(pnu, current_user["sub"])
    return {
        "is_liked": is_liked,
        "message": "관심 토지로 등록되었습니다." if is_liked else "관심 토지에서 해제되었습니다."
    }


@router.get("/lands", response_model=FavoriteListResponse)
def get_favorite_lands(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service)
):
    """
    사용자 좋아요 토지 목록
    
    - 페이지네이션 지원
    """
    return favorite_service.get_favorite_lands(
        user_email=current_user["sub"],
        skip=skip,
        limit=limit
    )