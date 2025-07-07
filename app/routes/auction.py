from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import JWTBearer
from app.enums.response import Status
from app.services.land.auction import auction_service
from app.schemas import APIResponse, error, auction

auction_router = APIRouter(prefix="/auction")


@auction_router.get(
    "/get-data",
    response_model=APIResponse[auction.LandAuctions],
    responses=error.make_error_responses(),
    summary="토지 경매 목록 조회",
    description="시도/시군구를 기준으로 올라와있는 경매 목록을 조회합니다.",
)
def get_auction_data(
    request: auction.GetAuctionRequest = Depends(),
    db: Session = Depends(get_db),
):
    auctions = auction_service.get_auction_data(pnu_prefix=request.pnu_prefix, page=request.page, size=request.size, db=db)
    return APIResponse[auction.LandAuctions](
        status=Status.SUCCESS,
        message="해당 지역의 경매 데이터를 성공적으로 불러왔습니다.",
        data=auctions,
	)

@auction_router.get(
    "/get-marker",
    response_model=APIResponse[List[auction.AuctionMarker]],
    summary="토지 매물 마커 조회",
    description="영역 내의 토지 경매 마커를 조회합니다.",
)
def get_auction_marker(
    request: auction.GetAuctionMarkerRequest = Depends(),
    db: Session = Depends(get_db)
):
    data = auction_service.get_auction_marker(
        req=request,
        db=db
    )
    return APIResponse[List[auction.AuctionMarker]](
        status=Status.SUCCESS,
        message="영역 내 토지 경매 마커를 조회하였습니다.",
        data=data,
    )