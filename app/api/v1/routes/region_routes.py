# api/v1/routes/region_routes.py
# 아직 리뷰 안끝남
"""
지역 정보 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.services.region_service import RegionService
from app.repositories.region_repository import RegionRepository
from app.schemas.region_schema import (
    RegionMarkerResponse,
    RegionDetailResponse,
    RegionLandListResponse,
)

router = APIRouter(prefix="/regions", tags=["Regions"])


def get_region_service(db: Session = Depends(get_db)) -> RegionService:
    return RegionService(region_repo=RegionRepository(db))


@router.get("/markers", response_model=RegionMarkerResponse)
def get_region_markers(
    min_lat: float,
    min_lng: float,
    max_lat: float,
    max_lng: float,
    zoom: int,
    region_service: RegionService = Depends(get_region_service)
):
    """지역 마커 조회"""
    return region_service.get_markers(min_lat, min_lng, max_lat, max_lng, zoom)


@router.get("/{pnu}", response_model=RegionDetailResponse)
def get_region_detail(
    pnu: str,
    region_service: RegionService = Depends(get_region_service)
):
    """지역 상세 정보"""
    return region_service.get_region_detail(pnu)


@router.get("/{pnu}/lands", response_model=RegionLandListResponse)
def get_region_lands(
    pnu: str,
    sort_type: str = Query("price", regex="^(price|area|recent)$"),
    page: int = Query(1, ge=1),
    region_service: RegionService = Depends(get_region_service)
):
    """지역 내 토지 목록"""
    return region_service.get_region_lands(pnu, sort_type, page)