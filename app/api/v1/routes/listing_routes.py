from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, get_current_user_optional
from app.services.listing_service import ListingService
from app.repositories.listing_repository import ListingRepository
from app.repositories.owner_repository import OwnerRepository
from app.repositories.user_repository import UserRepository
from app.dto.listing_dto import (
    ListingListResponse,
    ListingMarkerDTO,
    CreateListingRequest,
)

router = APIRouter()


def get_listing_service(db: Session = Depends(get_db)) -> ListingService:
    """ListingService 의존성 주입"""
    return ListingService(
        listing_repo=ListingRepository(db),
        owner_repo=OwnerRepository(db),
        user_repo=UserRepository(db)
    )


@router.get("", response_model=ListingListResponse)
def get_listings(
    pnu: str = Query(..., description="지역 PNU (2, 5, 8자리)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict | None = Depends(get_current_user_optional),
    listing_service: ListingService = Depends(get_listing_service)
):
    """매물 목록 조회"""
    user_email = current_user["sub"] if current_user else None
    
    return listing_service.get_listings(
        pnu_prefix=pnu,
        page=page,
        size=size,
        user_email=user_email
    )


@router.get("/markers", response_model=list[ListingMarkerDTO])
def get_listing_markers(
    min_lat: float,
    min_lng: float,
    max_lat: float,
    max_lng: float,
    listing_service: ListingService = Depends(get_listing_service)
):
    """매물 마커 조회 (지도 영역)"""
    return listing_service.get_listing_markers(
        min_lat=min_lat,
        min_lng=min_lng,
        max_lat=max_lat,
        max_lng=max_lng
    )


@router.post("")
def register_listing(
    request: CreateListingRequest,
    current_user: dict = Depends(get_current_user),
    listing_service: ListingService = Depends(get_listing_service)
):
    """매물 등록"""
    listing_service.register_listing(request, current_user["sub"])
    return {"message": "매물이 등록되었습니다."}


@router.delete("/{pnu}")
def remove_listing(
    pnu: str,
    current_user: dict = Depends(get_current_user),
    listing_service: ListingService = Depends(get_listing_service)
):
    """매물 삭제"""
    listing_service.remove_listing(pnu, current_user["sub"])
    return {"message": "매물이 삭제되었습니다."}
