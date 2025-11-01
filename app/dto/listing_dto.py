from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

from app.dto.land_dto import AddressDTO


class ListingDTO(BaseModel):
    """매물 상세 정보 DTO"""
    pnu: str
    address: AddressDTO
    lat: float
    lng: float
    area: float
    price: int
    summary: str
    reg_date: datetime
    is_my_land: bool = False
    nickname: str
    
    class Config:
        from_attributes = True


class ListingMarkerDTO(BaseModel):
    """매물 마커 DTO"""
    pnu: str
    address: AddressDTO
    lat: float
    lng: float
    area: float
    price: int
    reg_date: datetime
    
    class Config:
        from_attributes = True


class ListingListResponse(BaseModel):
    """매물 목록 응답"""
    listings: List[ListingDTO]
    page: int
    size: int
    total: int


class CreateListingRequest(BaseModel):
    """매물 등록 요청"""
    pnu: str = Field(..., description="PNU 코드")
    lat: float
    lng: float
    area: float = Field(..., gt=0, description="면적 (㎡)")
    price: int = Field(..., gt=0, description="가격")
    summary: str = Field(..., min_length=1, max_length=500, description="매물 설명")