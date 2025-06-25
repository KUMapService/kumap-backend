from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.enums.types import MapZoomLevel
from app.models.geo import RegionCoordinate, RegionStat
from app.schemas import region


class RegionService:
    def get_region_markers(self, lat1, lng1, lat2, lng2, zoom, db: Session) -> List[region.RegionData]:
        t = "eupmyeondong"
        if zoom in MapZoomLevel.HIGH:
            t = "sigungu"
        elif zoom in MapZoomLevel.TOP:
            t = "sido"

        items = db.query(RegionCoordinate).filter(
            and_(
                RegionCoordinate.lat.between(lat1, lat2),
                RegionCoordinate.lng.between(lng1, lng2),
                RegionCoordinate.type == t,
            )
        ).all()

        stats = {
            stat.pnu: stat
            for stat in db.query(RegionStat).filter(RegionStat.pnu.in_([item.pnu for item in items])).all()
        }

        data = []
        for item in items:
            stat = stats.get(item.pnu)
            data.append(region.RegionData(
                pnu=item.pnu,
                region=item.region,
                lat=item.lat,
                lng=item.lng,
                avg_predict_land_price=f"{stat.avg_predicted_price:.0f}" if stat else "0",
                price_ratio=f"{stat.price_ratio:.2f}" if stat else "0.00",
                total_land_count=stat.valid_count if stat else 0,
            ))
        return data

    def get_region_data(self, pnu: str, db: Session):
        item = db.query(RegionCoordinate).filter(RegionCoordinate.pnu == pnu).first()
        stat = db.query(RegionStat).filter_by(pnu=pnu).first()

        return region.RegionData(
            pnu=pnu,
            region=item.region,
            lat=item.lat,
            lng=item.lng,
            avg_predict_land_price=f"{stat.avg_predicted_price:.0f}" if stat else "0",
            price_ratio=f"{stat.price_ratio:.2f}" if stat else "0.00",
            total_land_count=stat.valid_count if stat else 0,
        )


region_service = RegionService()
