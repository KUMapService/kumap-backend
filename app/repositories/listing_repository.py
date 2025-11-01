from typing import List, Tuple
from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_

from app.models.land_model import LandListing, LandOwner
from app.repositories.base_repository import BaseRepository


class ListingRepository(BaseRepository[LandListing]):
    """매물 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(LandListing, db)
    
    def find_by_pnu(self, pnu: str) -> LandListing | None:
        """
        PNU로 매물 조회
        
        Args:
            pnu: PNU 코드
        
        Returns:
            LandListing or None
        """
        return (
            self.db.query(LandListing)
            .filter(LandListing.pnu == pnu)
            .first()
        )
    
    def find_by_user_id(self, user_id: int) -> List[LandListing]:
        """
        사용자가 등록한 매물 목록
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            매물 리스트
        """
        return (
            self.db.query(LandListing)
            .filter(LandListing.user_id == user_id)
            .all()
        )
    
    def find_by_region_with_owner(self, pnu_prefix: str, skip: int = 0, limit: int = 20) -> Tuple[List[Tuple[LandListing, LandOwner]], int]:
        """
        지역별 매물 목록 (소유주 정보 포함)
        
        Args:
            pnu_prefix: 지역 PNU 접두사 (2, 5, 8자리)
            skip: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            ([(LandListing, LandOwner), ...], total_count)
        """
        LandOwnerAlias = aliased(LandOwner)
        
        query = (
            self.db.query(LandListing, LandOwnerAlias)
            .join(LandOwnerAlias, LandListing.owner_id == LandOwnerAlias.owner_id)
            .filter(LandOwnerAlias.pnu.like(f"{pnu_prefix}%"))
        )
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    def find_by_bbox_with_owner(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> List[Tuple[LandListing, LandOwner]]:
        """
        지도 영역 내 매물 마커 조회
        
        Args:
            min_lat: 최소 위도
            min_lng: 최소 경도
            max_lat: 최대 위도
            max_lng: 최대 경도
        
        Returns:
            [(LandListing, LandOwner), ...]
        """
        return (
            self.db.query(LandListing, LandOwner)
            .join(LandOwner, LandListing.owner_id == LandOwner.owner_id)
            .filter(
                and_(
                    LandOwner.lat >= min_lat,
                    LandOwner.lat <= max_lat,
                    LandOwner.lng >= min_lng,
                    LandOwner.lng <= max_lng
                )
            )
            .all()
        )
    
    def create_listing(
        self,
        user_id: int,
        owner_id: int,
        pnu: str,
        lat: float,
        lng: float,
        area: float,
        price: int,
        summary: str
    ) -> LandListing:
        """
        매물 생성
        
        Args:
            user_id: 사용자 ID
            owner_id: 소유주 ID
            pnu: PNU 코드
            lat: 위도
            lng: 경도
            area: 면적
            price: 가격
            summary: 요약
        
        Returns:
            생성된 LandListing
        """
        listing = LandListing(
            user_id=user_id,
            owner_id=owner_id,
            pnu=pnu,
            lat=lat,
            lng=lng,
            area=area,
            price=price,
            summary=summary,
        )
        return self.create(listing)
    
    def exists_by_pnu(self, pnu: str) -> bool:
        """
        매물 존재 여부
        
        Args:
            pnu: PNU 코드
        
        Returns:
            존재 여부
        """
        return (
            self.db.query(LandListing)
            .filter(LandListing.pnu == pnu)
            .count() > 0
        )