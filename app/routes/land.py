from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import JWTBearer
from app.services.land import land_service
from app.schemas import APIResponse, land

land_router = APIRouter(prefix="/land")


@land_router.get(
    "/get-land-data",
    response_model=land.GetLandDataResponse,
    summary="토지 정보 조회",
    description="PNU를 기반으로 해당 토지의 정보와 사용자 좋아요 여부, 총 좋아요 수를 조회합니다.",
)
def get_land_data(
    request: land.GetLandRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    return land_service.get_land_detail(request.pnu, payload, db)

@land_router.get(
    "/get-land-predicted-price",
    response_model=land.GetLandPredictedPriceResponse,
    summary="토지 예측가 조회",
    description="PNU를 기반으로 해당 토지의 최신 예측가를 조회합니다.",
)
def get_land_predicted_price(
    request: land.GetLandRequest = Depends(), db: Session = Depends(get_db)
):
    return land_service.get_predict_price(request.pnu, db)

@land_router.get(
    "/get-land-report",
    response_model=land.GetLandReportResponse,
    summary="토지 분석 리포트 생성",
    description="PNU를 기반으로 토지 분석 보고서를 생성하거나 조회합니다. (LLM 사용)",
)
def get_land_report(
    request: land.GetLandRequest = Depends(), db: Session = Depends(get_db)
):
    return land_service.get_land_report(request.pnu, db)
