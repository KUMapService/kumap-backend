from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models.land_model import LandInfo
from app.exceptions.land_exceptions import (
    LandNotFoundException,
    OwnerAlreadyExistsException,
    OwnerNotFoundException,
)
from app.dto.land_dto import LandFeatureDTO



class LandRepository(BaseRepository[LandInfo]):
    def __init__(self, db: Session):
        super().__init__(LandInfo, db)
    
    def find_by_pnu(self, pnu: str) -> Optional[LandInfo]:
        """PNU로 토지 조회"""
        return self.db.query(LandInfo).filter(LandInfo.pnu == pnu).first()
    
    def create_from_feature(self, pnu: str, lat: float, lng: float, land_feature: LandFeatureDTO, use_plan: str) -> LandInfo:
        """외부 API 데이터로 토지 생성"""
        land = LandInfo(
            pnu=pnu,
            lat=lat,
            lng=lng,
            official_price=land_feature.official_price,
            land_reg=land_feature.land_reg,
            land_cls=land_feature.land_cls,
            land_zoning=land_feature.land_zoning,
            land_usage=land_feature.land_usage,
            land_area=land_feature.land_area,
            land_height=land_feature.land_height,
            land_form=land_feature.land_form,
            road_side=land_feature.road_side,
            use_plan=use_plan,
            stdr_year=land_feature.stdr_year,
            stdr_month=land_feature.stdr_month,
            like_count=0,
        )
        return self.create(land)
    
    def update_predicted_price(self, pnu: str, predicted_price: int, last_predicted_date: datetime) -> LandInfo:
        """예측가 업데이트"""
        land = self.find_by_pnu(pnu)
        if not land:
            raise LandNotFoundException(pnu)
        
        land.predicted_price = predicted_price
        land.last_predicted_date = last_predicted_date
        
        return self.update(land)
    
    def register_owner(self, pnu: str, user_id: int) -> None:
        """소유주 등록"""
        from app.models.land_model import LandOwner
        
        # 이미 등록되어 있는지 확인
        existing = (
            self.db.query(LandOwner)
            .filter(LandOwner.pnu == pnu, LandOwner.user_id == user_id)
            .first()
        )
        
        if existing:
            raise OwnerAlreadyExistsException()
        
        owner = LandOwner(pnu=pnu, user_id=user_id)
        self.db.add(owner)
        self.db.commit()
    
    def remove_owner(self, pnu: str, user_id: int) -> None:
        """소유주 해제"""
        from app.models.land_model import LandOwner
        
        owner = (
            self.db.query(LandOwner)
            .filter(LandOwner.pnu == pnu, LandOwner.user_id == user_id)
            .first()
        )
        
        if not owner:
            raise OwnerNotFoundException()
        
        self.db.delete(owner)
        self.db.commit()

    