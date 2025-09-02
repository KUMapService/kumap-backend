from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import JWTBearer
from app.db.session import get_db
from app.enums.response import Status
from app.schemas import APIResponse, error, land
from app.services.land import land_service

land_router = APIRouter(prefix="/land")


@land_router.get(
    "/get-data",
    response_model=APIResponse[land.LandData],
    responses=error.make_error_responses(need_404=True),
    summary="토지 정보 조회",
    description="PNU를 기반으로 해당 토지의 정보와 사용자 좋아요 여부, 총 좋아요 수를 조회합니다.",
)
def get_land_data(
    request: land.GetLandRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    data, is_like = land_service.get_land_detail(pnu=request.pnu, payload=payload, db=db)
    return APIResponse[land.LandData](
        status=Status.SUCCESS,
        message="해당 토지의 데이터를 성공적으로 불러왔습니다.",
        data=land.LandData(
            pnu=data.pnu,
            address=data.address,
            lat=data.lat,
            lng=data.lng,
            predicted_price=data.predicted_price,
            last_predicted_date=data.last_predicted_date,
            detail=data.detail,
            land_trade_list=data.land_trade_list,
            auction=data.auction,
            listing=data.listing,
            like_count=data.like_count,
            is_like=is_like,
        )
    )


@land_router.get(
    "/get-predicted-price",
    response_model=APIResponse[land.PredictedPriceData],
    responses=error.make_error_responses(need_404=True),
    summary="토지 예측가 조회",
    description="PNU를 기반으로 해당 토지의 최신 예측가를 조회합니다.",
)
def get_land_predicted_price(
    request: land.GetLandRequest = Depends(),
    db: Session = Depends(get_db)
):
    data = land_service.get_predict_price(pnu=request.pnu, db=db)
    return APIResponse[land.PredictedPriceData](
        status=Status.SUCCESS,
        message="토지 예측가를 성공적으로 불러왔습니다.",
        data=data,
    )

@land_router.get(
    "/get-report",
    response_model=APIResponse[land.LandReportData],
    summary="토지 분석 리포트 생성",
    description="PNU를 기반으로 토지 분석 보고서를 생성하거나 조회합니다. (LLM 사용)",
)
def get_land_report(
    request: land.GetLandRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    data = land_service.get_land_report(pnu=request.pnu, payload=payload, db=db)
    
    return APIResponse[land.LandReportData](
        status=Status.SUCCESS,
        message="토지 분석서를 성공적으로 불러왔습니다.",
        data=data,
    )

