from sqlalchemy.orm import Session
from typing import List, Tuple, Optional

from app.models.user_model import UserFavoriteLand
from app.models.land_model import LandInfo
from app.repositories.base_repository import BaseRepository


class FavoriteRepository(BaseRepository[UserFavoriteLand]):
    """좋아요 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(UserFavoriteLand, db)
    
    def find_by_user_and_pnu(self, user_id: int, pnu: str) -> Optional[UserFavoriteLand]:
        """
        사용자와 PNU로 좋아요 조회
        
        Args:
            user_id: 사용자 ID
            pnu: PNU 코드
        
        Returns:
            UserFavoriteLand or None
        """
        return (
            self.db.query(UserFavoriteLand)
            .filter(
                UserFavoriteLand.user_id == user_id,
                UserFavoriteLand.pnu == pnu
            )
            .first()
        )
    
    def exists(self, user_id: int, pnu: str) -> bool:
        """
        좋아요 존재 여부
        
        Args:
            user_id: 사용자 ID
            pnu: PNU 코드
        
        Returns:
            존재 여부
        """
        return (
            self.db.query(UserFavoriteLand)
            .filter(
                UserFavoriteLand.user_id == user_id,
                UserFavoriteLand.pnu == pnu
            )
            .count() > 0
        )
    
    def get_user_favorites(self, user_id: int) -> List[UserFavoriteLand]:
        """
        사용자의 모든 좋아요 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            좋아요 목록
        """
        return (
            self.db.query(UserFavoriteLand)
            .filter(UserFavoriteLand.user_id == user_id)
            .all()
        )
    
    def get_user_favorite_pnus(self, user_id: int) -> List[str]:
        """
        사용자가 좋아요한 PNU 목록
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            PNU 코드 리스트
        """
        results = (
            self.db.query(UserFavoriteLand.pnu)
            .filter(UserFavoriteLand.user_id == user_id)
            .all()
        )
        return [pnu for (pnu,) in results]
    
    def get_user_favorites_with_lands(self, user_id: int, skip: int = 0, limit: int = 20) -> Tuple[List[Tuple[UserFavoriteLand, LandInfo]], int]:
        """
        사용자 좋아요 목록 (토지 정보 포함)
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            (좋아요+토지 정보 리스트, 전체 개수)
        """
        query = (
            self.db.query(UserFavoriteLand, LandInfo)
            .join(LandInfo, UserFavoriteLand.pnu == LandInfo.pnu)
            .filter(UserFavoriteLand.user_id == user_id)
        )
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    def create_favorite(self, user_id: int, pnu: str) -> UserFavoriteLand:
        """
        좋아요 생성
        
        Args:
            user_id: 사용자 ID
            pnu: PNU 코드
        
        Returns:
            생성된 UserFavoriteLand
        """
        favorite = UserFavoriteLand(user_id=user_id, pnu=pnu)
        return self.create(favorite)
    
    def delete_favorite(self, user_id: int, pnu: str) -> bool:
        """
        좋아요 삭제
        
        Args:
            user_id: 사용자 ID
            pnu: PNU 코드
        
        Returns:
            삭제 성공 여부
        """
        favorite = self.find_by_user_and_pnu(user_id, pnu)
        
        if not favorite:
            return False
        
        self.delete(favorite)
        return True
    
    def count_by_pnu(self, pnu: str) -> int:
        """
        특정 토지의 좋아요 개수
        
        Args:
            pnu: PNU 코드
        
        Returns:
            좋아요 개수
        """
        return (
            self.db.query(UserFavoriteLand)
            .filter(UserFavoriteLand.pnu == pnu)
            .count()
        )
    
    def get_top_favorited_lands(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        좋아요 많은 토지 순위
        
        Args:
            limit: 가져올 개수
        
        Returns:
            [(pnu, like_count), ...]
        """
        from sqlalchemy import func
        
        results = (
            self.db.query(
                UserFavoriteLand.pnu,
                func.count(UserFavoriteLand.user_id).label('like_count')
            )
            .group_by(UserFavoriteLand.pnu)
            .order_by(func.count(UserFavoriteLand.user_id).desc())
            .limit(limit)
            .all()
        )
        
        return [(pnu, count) for pnu, count in results]
