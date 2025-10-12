from typing import Optional
from sqlalchemy.orm import Session

from app.models.geo_model import GeometryData
from app.repositories.base_repository import BaseRepository


class GeoRepository(BaseRepository[GeometryData]):
    """지적도 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(GeometryData, db)
    
    def find_geometry_by_pnu(self, pnu: str) -> Optional[GeometryData]:
        """PNU로 지적도 데이터 조회"""
        return self.db.query(GeometryData).filter(GeometryData.pnu == pnu).first()
    
    def exists_by_pnu(self, pnu: str) -> bool:
        """PNU 존재 여부 확인"""
        return self.db.query(GeometryData).filter(GeometryData.pnu == pnu).count() > 0
