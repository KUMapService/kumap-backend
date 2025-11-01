
from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Session

from app.enums.types import MapZoomLevel, SortType
from app.models.geo_model import RegionCoordinate, RegionStat
from app.models.land_model import LandInfo
from app.schemas import land, region
from app.utils.convert_code import code2addr


class RegionService:
    def get_region_markers(self, lat1, lng1, lat2, lng2, zoom, db: Session) -> list[region.RegionData]:
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
                avg_official_price=f"{stat.avg_official_price:.0f}" if stat else "0",
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
            avg_official_price=f"{stat.avg_official_price:0f}" if stat else "0",
            price_ratio=f"{stat.price_ratio:.2f}" if stat else "0.00",
            total_land_count=stat.valid_count if stat else 0,
        )

    def get_region_land_list(self, pnu: str, sort_type: SortType, page: int, db: Session) -> list[land.LandData]:
        PAGE_SIZE = 10
        offset = (page - 1) * PAGE_SIZE

        query = db.query(LandInfo).filter(LandInfo.pnu.like(f"{pnu}%"))

        # 정렬 조건 분기
        if sort_type == SortType.PRICE_DESC:
            query = query.order_by(desc(LandInfo.predicted_price))
        elif sort_type == SortType.PRICE_ASC:
            query = query.order_by(asc(LandInfo.predicted_price))
        elif sort_type == SortType.LIKE_DESC:
            query = query.order_by(desc(LandInfo.like_count))
        else:  # default_order
            query = query.order_by(LandInfo.pnu)

        # 페이징 적용
        items = query.offset(offset).limit(PAGE_SIZE).all()

        data = []
        for item in items:
            data.append(
                land.LandSimpleData(
                    pnu=item.pnu,
                    address=code2addr(item.pnu, dict_format=True),
                    lat=item.lat,
                    lng=item.lng,
                    predicted_price=item.predicted_price,
                    price_ratio=item.official_price,
                    land_cls=item.land_cls,
                    land_zoning=item.land_zoning,
                    last_predicted_date=item.last_predicted_date,
                    like_count=item.like_count,
                    is_like=False,
                    is_auction=True,
                    is_listing=True,
                )
            )
        return data

region_service = RegionService()
