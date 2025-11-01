# api/v1/routes/auction_routes.py
# 아직 리뷰 안끝남
"""
경매 정보 API
"""
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.enums.response import Status
from app.schemas import APIResponse
from app.services.auction_service import AuctionService
from app.repositories.auction_repository import AuctionRepository
from app.schemas.auction_schema import (
    GetAuctionRequest, 
    GetAuctionMarkerRequest, 
    AuctionListResponse, 
    AuctionMarkerResponse
)

router = APIRouter()


def get_auction_service(db: Session = Depends(get_db)) -> AuctionService:
    return AuctionService(auction_repo=AuctionRepository(db))


@router.get("", response_model=APIResponse[AuctionListResponse])
def get_auction_list(
    request: GetAuctionRequest = Depends(),
    auction_service: AuctionService = Depends(get_auction_service)
):
    """경매 목록 조회"""
    auction_list, total = auction_service.get_auction_list(request.pnu, request.page, request.size)
    return APIResponse[AuctionListResponse](
        status=Status.SUCCESS,
        message="해당 지역의 경매 목록을 성공적으로 불러왔습니다.",
        data=AuctionListResponse(
            auctions=auction_list,
            page=request.page,
            size=request.size,
            total=total,
        ),
    )


@router.get("/markers", response_model=APIResponse[AuctionMarkerResponse])
def get_auction_markers(
    request: GetAuctionMarkerRequest = Depends(),
    auction_service: AuctionService = Depends(get_auction_service)
):
    """경매 마커 조회"""
    auction_marker_list = auction_service.get_auction_marker(request.min_lat, request.min_lng, request.max_lat, request.max_lng)
    return APIResponse[AuctionMarkerResponse](
        status=Status.SUCCESS,
        message="해당 지역의 경매 마커를 성공적으로 불러왔습니다.",
        data=AuctionMarkerResponse(
            markers=auction_marker_list,
        ),
    )