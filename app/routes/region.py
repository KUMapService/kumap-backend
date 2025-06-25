from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import JWTBearer
from app.enums.response import Status
from app.services.region import region_service
from app.schemas import APIResponse, error, region

region_router = APIRouter(prefix="/region")


@region_router.get(
    "/get-region_markers",
    response_model=APIResponse[List[region.RegionData]],
    responses=error.make_error_responses(need_404=True),
    summary="지역 마커 조회",
    description="지도 영역 bbox를 기준으로 지도 내 모든 지역 마커를 조회합니다.",
)
def get_region_markers(
    request: region.GetRegionMarkersRequest = Depends(),
    db: Session = Depends(get_db),
):
    data = region_service.get_region_markers(request.min_lat, request.min_lng, request.max_lat, request.max_lng, request.zoom, db=db)
    return APIResponse[List[region.RegionData]](
        status=Status.SUCCESS,
        message="범위 내 지역 마커를 불러왔습니다.",
        data=data
    )
    

@region_router.get(
    "/get-region_data",
    response_model=APIResponse[List[region.RegionData]],
    responses=error.make_error_responses(need_404=True),
    summary="지역 정보 조회",
    description="PNU 코드를 기반으로 해당 지역에 대한 정보를 조회합니다.",
)
def get_region_data(
    request: region.GetRegionDataRequest = Depends(),
    db: Session = Depends(get_db),
):
    data = region_service.get_region_markers(request.pnu, db=db)
    return APIResponse[region.RegionData](
        status=Status.SUCCESS,
        message="범위 내 지역 마커를 불러왔습니다.",
        data=data
    )
