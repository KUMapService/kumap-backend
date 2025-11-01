from typing import List
from sqlalchemy.orm import Session

from app.models.land_model import LandOwner
from app.repositories.base_repository import BaseRepository


class OwnerRepository(BaseRepository[LandOwner]):
    """토지 소유주 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(LandOwner, db)
    
    def find_by_pnu(self, pnu: str) -> LandOwner | None:
        """
        PNU로 소유주 조회
        
        Args:
            pnu: PNU 코드
        
        Returns:
            LandOwner or None
        """
        return (
            self.db.query(LandOwner)
            .filter(LandOwner.pnu == pnu)
            .first()
        )
    
    def find_by_pnu_and_user(
        self,
        pnu: str,
        user_id: int
    ) -> LandOwner | None:
        """
        PNU와 사용자로 소유주 조회
        
        Args:
            pnu: PNU 코드
            user_id: 사용자 ID
        
        Returns:
            LandOwner or None
        """
        return (
            self.db.query(LandOwner)
            .filter(
                LandOwner.pnu == pnu,
                LandOwner.user_id == user_id
            )
            .first()
        )
    
    def find_by_user_id(self, user_id: int) -> List[LandOwner]:
        """
        사용자가 소유한 토지 목록
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            LandOwner 리스트
        """
        return (
            self.db.query(LandOwner)
            .filter(LandOwner.user_id == user_id)
            .all()
        )
    
    def create_owner(
        self,
        pnu: str,
        user_id: int,
        lat: float,
        lng: float
    ) -> LandOwner:
        """
        소유주 생성
        
        Args:
            pnu: PNU 코드
            user_id: 사용자 ID
            lat: 위도
            lng: 경도
        
        Returns:
            생성된 LandOwner
        """
        owner = LandOwner(
            pnu=pnu,
            user_id=user_id,
            lat=lat,
            lng=lng
        )
        return self.create(owner)
    
    def exists_by_pnu(self, pnu: str) -> bool:
        """
        소유주 등록 여부
        
        Args:
            pnu: PNU 코드
        
        Returns:
            존재 여부
        """
        return (
            self.db.query(LandOwner)
            .filter(LandOwner.pnu == pnu)
            .count() > 0
        )
    
    def is_owner(self, pnu: str, user_id: int) -> bool:
        """
        사용자가 해당 토지의 소유주인지 확인
        
        Args:
            pnu: PNU 코드
            user_id: 사용자 ID
        
        Returns:
            소유주 여부
        """
        return (
            self.db.query(LandOwner)
            .filter(
                LandOwner.pnu == pnu,
                LandOwner.user_id == user_id
            )
            .count() > 0
        )