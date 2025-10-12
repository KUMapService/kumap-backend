from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.types import Numeric

from app.core.database import Base


class GeometryData(Base):
    """
    📦 지적도(Geometry) 테이블

    - PNU 기준으로 특정 행정구역 또는 단일 필지의 좌표 정보를 저장
    - 중심좌표(lat, lng) 및 GeoJSON 형태의 다각형 좌표를 함께 보유
    """

    __tablename__ = "geometry_data"

    pnu = Column(
        String(10), primary_key=True, nullable=False,
        comment="PNU 코드 (행정구역 또는 개별 필지 식별자)",
    )

    centroid_lat = Column(
        Numeric(17, 14), nullable=False,
        comment="중심 위도 (Latitude) - 소수점 14자리까지 정밀도 확보",
    )

    centroid_lng = Column(
        Numeric(17, 14), nullable=False,
        comment="중심 경도 (Longitude) - 소수점 14자리까지 정밀도 확보",
    )

    multi_polygon = Column(
        LONGTEXT, nullable=False,
        comment="다각형 좌표 (GeoJSON 형식의 MultiPolygon 문자열)",
    )

    def __repr__(self):
        return (
            f"<GeometryData(pnu={self.pnu}, "
            f"centroid_lat={self.centroid_lat}, "
            f"centroid_lng={self.centroid_lng})>"
        )

class RegionCoordinate(Base):
    """
    🗺️ 행정구역 중심 좌표 테이블 (RegionCoordinate)

    - 시도/시군구/읍면동 단위의 행정구역 중심 위경도 좌표 저장
    - 좌표계는 WGS84 기준 (위도/경도)
    """

    __tablename__ = "region_coordinate"

    pnu = Column(
        String(10), primary_key=True, nullable=False,
        comment="PNU 코드 (행정구역 고유 식별자)"
    )
    type = Column(
        String(12), nullable=False,
        comment="행정구역 타입 (sido/sigungu/eupmyeondong)"
    )
    region = Column(
        String(50), nullable=False,
        comment="행정구역 명 (ex: 서울특별시 강남구 역삼동)"
    )
    lat = Column(
        Numeric(17, 14), nullable=False,
        comment="위도 (Latitude)"
    )
    lng = Column(
        Numeric(17, 14), nullable=False,
        comment="경도 (Longitude)"
    )

    def __repr__(self):
        return (
            f"<RegionCoordinate(pnu={self.pnu}, region={self.region}, "
            f"lat={self.lat}, lng={self.lng})>"
        )

class RegionStat(Base):
    """
    📊 행정구역 통계 데이터 테이블

    - 행정구역(PNU prefix)에 대한 예측가 및 공시지가 통계를 저장
    - 클러스터링 시 계산 비용을 줄이기 위한 사전 계산 캐시 테이블
    """

    __tablename__ = "region_stat"

    pnu = Column(
        String(10), primary_key=True, nullable=False,
        comment="행정구역 PNU prefix (10자리)",
    )
    avg_predicted_price = Column(
        Float, nullable=False, default=0,
        comment="해당 행정구역의 평균 예측 토지가격 (원)",
    )
    avg_official_price = Column(
        Float, nullable=False, default=0,
        comment="해당 행정구역의 평균 공시지가 (원)",
    )
    price_ratio = Column(
        Float, nullable=False, default=0,
        comment="예측가 / 공시지가 비율 (%)",
    )
    valid_count = Column(
        Integer, nullable=False, default=0,
        comment="유효한 예측가를 가진 토지 수 (0 초과, None 제외)",
    )

    def __repr__(self):
        return (
            f"<RegionStat(pnu={self.pnu}, avg_price={self.avg_predicted_price}, "
            f"ratio={self.price_ratio}%)>"
        )
