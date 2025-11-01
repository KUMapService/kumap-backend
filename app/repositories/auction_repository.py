from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.land_model import LandAuction
from app.repositories.base_repository import BaseRepository


class AuctionRepository(BaseRepository[LandAuction]):
    """토지 경매 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(LandAuction, db)
    
    def find_by_pnu_prefix(self, pnu_prefix: str, offset: int = 0, limit: int = 100) -> Tuple[List[LandAuction], int]:
        """
        PNU 접두사로 경매 목록 조회
        
        Args:
            pnu_prefix: PNU 접두사 (2, 5, 8자리)
            offset: 건너뛸 개수
            limit: 가져올 개수
        
        Returns:
            (경매 목록, 전체 개수)
        """
        query = (
            self.db.query(LandAuction)
            .filter(LandAuction.pnu.like(f"{pnu_prefix}%"))
        )
        
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        
        return items, total
    
    def find_by_bbox(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> List[LandAuction]:
        """
        지도 영역 내 경매 마커 조회
        
        Args:
            min_lat: 최소 위도
            min_lng: 최소 경도
            max_lat: 최대 위도
            max_lng: 최대 경도
        
        Returns:
            경매 목록
        """
        return (
            self.db.query(LandAuction)
            .filter(
                and_(
                    LandAuction.lat >= min_lat,
                    LandAuction.lat <= max_lat,
                    LandAuction.lng >= min_lng,
                    LandAuction.lng <= max_lng
                )
            )
            .all()
        )
    
    def find_by_doc_id(self, doc_id: str) -> LandAuction | None:
        """
        doc_id로 경매 조회
        
        Args:
            doc_id: 경매 고유 ID
        
        Returns:
            LandAuction or None
        """
        return (
            self.db.query(LandAuction)
            .filter(LandAuction.doc_id == doc_id)
            .first()
        )
    
    def exists_by_doc_id(self, doc_id: str) -> bool:
        """
        경매 존재 여부
        
        Args:
            doc_id: 경매 고유 ID
        
        Returns:
            존재 여부
        """
        return (
            self.db.query(LandAuction)
            .filter(LandAuction.doc_id == doc_id)
            .count() > 0
        )

