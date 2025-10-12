from typing import List, Optional
from pydantic import BaseModel, Field


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