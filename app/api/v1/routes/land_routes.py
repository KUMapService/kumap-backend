from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, Dict

from app.core.dependencies import get_db, get_current_user_optional, get_current_user
from app.enums.response import Status
from app.schemas import APIResponse
from app.services.land_service import LandService
from app.repositories.land_repository import LandRepository
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.user_repository import UserRepository
from app.schemas.land_schema import (
    LandDetailResponse,
    LandDetail,
    LandTrade,
    PredictedPriceResponse,
)

router = APIRouter()


def get_land_service(db: Session = Depends(get_db)) -> LandService:
    """LandService 의존성 주입"""
    return LandService(
        land_repo=LandRepository(db),
        favorite_repo=FavoriteRepository(db),
        user_repo=UserRepository(db)
    )


@router.get("/{pnu}", response_model=APIResponse[LandDetailResponse])
def get_land_detail(
    pnu: str,
    current_user: Optional[Dict] = Depends(get_current_user_optional),
    land_service: LandService = Depends(get_land_service)
):
    """
    토지 상세 정보 조회
    
    - PNU 코드로 토지 상세 정보 조회
    - 좋아요 여부 포함 (로그인 시)
    """
    land_detail_dto = land_service.get_land_detail(
        pnu, 
        current_user["sub"] if current_user else None
    )
    
    # DTO를 Response로 변환
    land_detail_response = LandDetailResponse(
        pnu=land_detail_dto.pnu,
        address=land_detail_dto.address,
        lat=land_detail_dto.lat,
        lng=land_detail_dto.lng,
        predicted_price=land_detail_dto.predicted_price,
        last_predicted_date=land_detail_dto.last_predicted_date,
        detail=LandDetail(
            official_price=land_detail_dto.official_price,
            land_reg=land_detail_dto.land_reg,
            land_cls=land_detail_dto.land_cls,
            land_zoning=land_detail_dto.land_zoning,
            land_usage=land_detail_dto.land_usage,
            land_area=land_detail_dto.land_area,
            land_height=land_detail_dto.land_height,
            land_form=land_detail_dto.land_form,
            road_side=land_detail_dto.road_side,
            use_plan=land_detail_dto.use_plan,
            stdr_year=land_detail_dto.stdr_year,
            stdr_month=land_detail_dto.stdr_month,
        ),
        land_trade_list=[],  # TODO: trade_history를 LandTrade로 변환
        auction=land_detail_dto.auction,
        listing=land_detail_dto.listing,
        like_count=land_detail_dto.like_count,
        is_like=land_detail_dto.is_liked if current_user else None,
    )
    
    return APIResponse[LandDetailResponse](
        status=Status.SUCCESS,
        message="토지 상세 정보를 성공적으로 불러왔습니다.",
        data=land_detail_response,
    )



@router.get("/{pnu}/predicted-price", response_model=APIResponse[PredictedPriceResponse])
def get_predicted_price(
    pnu: str,
    land_service: LandService = Depends(get_land_service)
):
    """
    토지 예측가 조회
    
    - 최신 AI 예측가 반환
    """
    land_detail_dto = land_service.get_land_detail(pnu, None)
    predicted_price = PredictedPriceResponse(
        predicted_price=land_detail_dto.predicted_price,
        last_predicted_date=land_detail_dto.last_predicted_date,
    )
    if predicted_price is None:
        predicted_data = land_price_predictor.predict(pnu=pnu, year=now.year, month=now.month)
        land_info.predicted_price = predicted_data.predicted_price
        land_info.last_predicted_date = predicted_data.last_predicted_date
        db.commit()
    return APIResponse[PredictedPriceResponse](
        status=Status.SUCCESS,
        message="토지 예측가를 성공적으로 불러왔습니다.",
        data=predicted_price,
    )


@router.post("/{pnu}/owner")
def register_owner(
    pnu: str,
    current_user: dict = Depends(get_current_user),
    land_service: LandService = Depends(get_land_service)
):
    """
    토지 소유주 등록
    
    - 로그인한 사용자를 해당 토지의 소유주로 등록
    """
    land_service.register_owner(pnu, current_user["sub"])
    return APIResponse(
        status=Status.SUCCESS,
        message="소유주 등록이 완료되었습니다.",
    )


@router.delete("/{pnu}/owner")
def remove_owner(
    pnu: str,
    current_user: dict = Depends(get_current_user),
    land_service: LandService = Depends(get_land_service)
):
    """토지 소유주 해제"""
    land_service.remove_owner(pnu, current_user["sub"])
    return APIResponse(
        status=Status.SUCCESS,
        message="소유주 등록이 해제되었습니다.",
    )
