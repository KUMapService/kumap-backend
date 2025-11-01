from typing import List

from app.dto.land_dto import LandSimpleDTO
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.land_repository import LandRepository
from app.repositories.user_repository import UserRepository
from app.exceptions.favorite_exceptions import (
    AlreadyFavoritedException,
    FavoriteNotFoundException,
)
from app.exceptions.land_exceptions import LandNotFoundException
from app.exceptions.user_exceptions import UserNotFoundException


class FavoriteService:
    """좋아요 서비스"""
    
    def __init__(
        self,
        favorite_repo: FavoriteRepository,
        land_repo: LandRepository,
        user_repo: UserRepository
    ):
        self.favorite_repo = favorite_repo
        self.land_repo = land_repo
        self.user_repo = user_repo
    
    def add_favorite(self, pnu: str, user_email: str) -> None:
        """
        토지 좋아요 추가
        
        Args:
            pnu: PNU 코드
            user_email: 사용자 이메일
        
        Raises:
            AlreadyFavoritedException: 이미 좋아요한 토지
            LandNotFoundException: 토지 없음
            UserNotFoundException: 사용자 없음
        """
        # 사용자 확인
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException()
        
        # 토지 확인
        land = self.land_repo.find_by_pnu(pnu)
        if not land:
            raise LandNotFoundException(pnu)
        
        # 이미 좋아요했는지 확인
        if self.favorite_repo.exists(user.user_id, pnu):
            raise AlreadyFavoritedException()
        
        # 좋아요 추가
        self.favorite_repo.create_favorite(user.user_id, pnu)
        
        # 토지 좋아요 수 증가
        self.land_repo.increment_like_count(land)
    
    def remove_favorite(self, pnu: str, user_email: str) -> None:
        """
        토지 좋아요 취소
        
        Args:
            pnu: PNU 코드
            user_email: 사용자 이메일
        
        Raises:
            FavoriteNotFoundException: 좋아요 없음
            UserNotFoundException: 사용자 없음
        """
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException()
        
        # 좋아요 삭제
        success = self.favorite_repo.delete_favorite(user.user_id, pnu)
        
        if not success:
            raise FavoriteNotFoundException()
        
        # 토지 좋아요 수 감소
        land = self.land_repo.find_by_pnu(pnu)
        if land:
            self.land_repo.decrement_like_count(land)
    
    def toggle_favorite(self, pnu: str, user_email: str) -> bool:
        """
        토지 좋아요 토글
        
        Args:
            pnu: PNU 코드
            user_email: 사용자 이메일
        
        Returns:
            좋아요 상태 (True: 추가됨, False: 제거됨)
        """
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException()
        
        # 토지 확인
        land = self.land_repo.find_by_pnu(pnu)
        if not land:
            raise LandNotFoundException(pnu)
        
        # 이미 좋아요했는지 확인
        existing = self.favorite_repo.find_by_user_and_pnu(user.user_id, pnu)
        
        if existing:
            # 좋아요 취소
            self.favorite_repo.delete(existing)
            self.land_repo.decrement_like_count(land)
            return False
        else:
            # 좋아요 추가
            self.favorite_repo.create_favorite(user.user_id, pnu)
            self.land_repo.increment_like_count(land)
            return True
    
    def get_favorite_lands(
        self,
        user_email: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[LandSimpleDTO]:
        """
        사용자 좋아요 토지 목록
        
        Args:
            user_email: 사용자 이메일
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            토지 목록
        """
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException()
        
        # 좋아요 + 토지 정보 조회
        favorites, total = self.favorite_repo.get_user_favorites_with_lands(
            user.user_id,
            skip,
            limit
        )
        
        # DTO 변환
        lands = []
        for favorite, land in favorites:
            lands.append(LandSimpleDTO(
                pnu=land.pnu,
                address=land.address,
                lat=land.lat,
                lng=land.lng,
                predicted_price=land.predicted_price,
                land_cls=land.land_cls,
                land_zoning=land.land_zoning,
                land_area=land.land_area,
                like_count=land.like_count,
            ))
        
        return lands
    
    def is_favorited(self, pnu: str, user_email: str) -> bool:
        """
        좋아요 여부 확인
        
        Args:
            pnu: PNU 코드
            user_email: 사용자 이메일
        
        Returns:
            좋아요 여부
        """
        user = self.user_repo.find_by_email(user_email)
        if not user:
            return False
        
        return self.favorite_repo.exists(user.user_id, pnu)
