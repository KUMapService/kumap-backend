from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import JWTBearer
from app.enums.response import Status
from app.services.land.listing import listing_service
from app.schemas import APIResponse, error, listing

listing_router = APIRouter(prefix="/listing")


@listing_router.get(
    "/get-listing",
    response_model=APIResponse[listing.LandListings],
    responses=error.make_error_responses(),
    summary="토지 매물 목록 조회",
    description="시도/시군구를 기준으로 올라와있는 매물 목록을 조회합니다.",
)
def get_listing_data(
    request: listing.GetListingRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    listings = listing_service.get_listing_data(pnu_prefix=request.pnu_prefix, page=request.page, size=request.size, payload=payload, db=db)
    return APIResponse[listing.LandListings](
        status=Status.SUCCESS,
        message="해당 지역의 매물 데이터를 성공적으로 불러왔습니다.",
        data=listings,
	)

@listing_router.get(
    "/get-marker",
    response_model=APIResponse[List[listing.ListingMarker]],
    summary="토지 매물 마커 조회",
    description="영역 내의 토지 매물 마커를 조회합니다.",
)
def get_listing_marker(
    request: listing.GetListingMarkerRequest = Depends(),
    db: Session = Depends(get_db)
):
    data = listing_service.get_listing_marker(
        req=request,
        db=db
    )
    return APIResponse[List[listing.ListingMarker]](
        status=Status.SUCCESS,
        message="영역 내 토지 매물 마커를 조회하였습니다.",
        data=data,
    )

@listing_router.get(
    "/register-listing",
    response_model=APIResponse,
    summary="토지 매물 등록",
    description="토지 매물을 등록합니다.",
)
def register_listing(
    request: listing.RegisterListingRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    listing_service.register_listing(req=request, payload=payload, db=db)
    return APIResponse(
        status=Status.SUCCESS,
        message="토지 매물을 등록했습니다.",
    )

@listing_router.get(
    "/remove-listing",
    response_model=APIResponse,
    responses=error.make_error_responses(need_401=True, need_404=True, need_422=True),
    summary="토지 매물 등록 해제",
    description="등록되어 있는 토지 매물을 제거합니다.",
)
def remove_listing(
    request: listing.RemoveListingRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    listing_service.remove_listing(pnu=request.pnu, payload=payload, db=db)
    return APIResponse(
        status=Status.SUCCESS,
        message="등록되어 있는 토지 매물을 제거했습니다.",
    )

