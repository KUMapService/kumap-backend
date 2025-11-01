from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.dto.geo_dto import AddressDTO


class LandFeatureDTO(BaseModel):
    """토지 특성 정보 DTO"""
    pnu: str
    legal_dong_code: str
    legal_dong: str
    land_reg_code: str
    land_reg: str
    land_lot_number: str
    stdr_year: str
    stdr_month: str
    land_cls_code: str
    land_cls: str
    land_area: float
    land_zoning_code: str
    land_zoning: str
    land_zoning2_code: str
    land_zoning2: str
    land_usage_code: str
    land_usage: str
    land_height_code: str
    land_height: str
    land_form_code: str
    land_form: str
    road_side_code: str
    road_side: str
    official_price: float
    last_update_date: Optional[str] = None


class FluctuationRateDTO(BaseModel):
    """땅값 변동률 DTO"""
    index: float = Field(..., description="지가 지수")
    change_rt: float = Field(..., description="변동률 (%)")
    accumulate_change_rt: float = Field(..., description="누적 변동률 (%)")


class LandUsePlanDTO(BaseModel):
    """토지 용도지역 계획 DTO"""
    plans: List[str] = Field(..., description="용도지역 목록")
    formatted: str = Field(..., description="포맷된 문자열")


class LandBasicDTO(BaseModel):
    """토지 기본 정보 DTO"""
    pnu: str
    address: AddressDTO
    lat: float
    lng: float
    predicted_price: Optional[int] = None
    last_predicted_date: Optional[datetime] = None
    like_count: int = 0
    
    class Config:
        from_attributes = True


class ListingDTO(BaseModel):
    """매물 정보 DTO"""
    pnu: str
    nickname: str
    lat: float
    lng: float
    area: float
    price: int
    summary: str
    reg_date: datetime
    is_my_land: bool = False
    
    class Config:
        from_attributes = True


class AuctionDTO(BaseModel):
    """경매 정보 DTO"""
    pnu: str
    lat: float
    lng: float
    case_cd: str
    obj_cd: str
    obj_type: str
    appraisal_price: int
    min_sale_price: int
    auction_date: datetime
    court_in_charge: str
    court_detail: str
    land_detail: str
    obj_list: List["AuctionObjectDTO"] = []
    
    class Config:
        from_attributes = True


class AuctionObjectDTO(BaseModel):
    """경매 물건 DTO"""
    pnu: str
    lat: float
    lng: float
    price: int
    auction_date: datetime


class TradeHistoryDTO(BaseModel):
    """거래 이력 DTO"""
    trade_date: datetime
    price: int
    area: float
    
    class Config:
        from_attributes = True


class LandDetailDTO(BaseModel):
    """토지 상세 정보 DTO"""
    pnu: str
    address: AddressDTO
    lat: float
    lng: float
    predicted_price: Optional[int] = None
    last_predicted_date: Optional[datetime] = None
    
    # 토지 특성
    official_price: float
    land_reg: str
    land_cls: str
    land_zoning: str
    land_usage: str
    land_area: float
    land_height: str
    land_form: str
    road_side: str
    use_plan: str
    stdr_year: str
    stdr_month: str
    
    # 좋아요
    like_count: int = 0
    is_liked: bool = False
    
    # 관계 데이터 (선택적)
    auction: Optional[AuctionDTO] = None
    listing: Optional[ListingDTO] = None
    trade_history: List[TradeHistoryDTO] = []
    
    class Config:
        from_attributes = True


class PredictedPriceDTO(BaseModel):
    """토지 예측가 DTO"""
    predicted_price: Optional[int] = None
    last_predicted_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LandSimpleDTO(BaseModel):
    """토지 간단 정보 DTO (목록용)"""
    pnu: str
    address: str
    lat: float
    lng: float
    predicted_price: Optional[int] = None
    land_cls: str
    land_zoning: str
    land_area: float
    like_count: int = 0
    
    class Config:
        from_attributes = True
