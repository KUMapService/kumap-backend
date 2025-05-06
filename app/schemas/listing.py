from pydantic import BaseModel, Field, NaiveDatetime
from typing import List, Optional

from app.schemas.geo import AddressSchema


# DATA SCHEMA
class Listing(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: Optional[AddressSchema] = Field(None, description="주소")
    nickname: str = Field(..., description="사용자 닉네임")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    area: float = Field(..., description="매물 면적")
    price: float = Field(..., description="매물 가격")
    summary: str = Field(..., description="매물 설명")
    reg_date: NaiveDatetime = Field(..., descript="매물 등록 일자")
    is_my_land: bool = Field(..., description="사용자 매물 여부")

class ListingMarker(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: Optional[AddressSchema] = Field(None, description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    area: float = Field(..., description="매물 면적")
    price: float = Field(..., description="매물 가격")
    reg_date: NaiveDatetime = Field(..., descript="매물 등록 일자")


# REQUEST DATA
class GetListingRequest(BaseModel):
    pnu_prefix: str = Field(..., description="PNU 코드 (2자리 or 5자리 or 8자리)")
    page: int = Field(..., description="조회할 페이지")
    size: int = Field(..., description="한 번에 받아올 데이터 크기")

class GetListingMarkerRequest(BaseModel):
    min_lat: float = Field(..., description="최소 위도 좌표")
    min_lng: float = Field(..., description="최소 경도 좌표")
    max_lat: float = Field(..., description="최대 위도 좌표")
    max_lng: float = Field(..., description="최대 경도 좌표")

class RegisterListingRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    area: float = Field(..., description="면적 (㎡)")
    price: float = Field(..., description="매물 가격")
    summary: str = Field(..., description="매물 요약 설명")

class RemoveListingRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")


# RESPONSE DATA
class LandListings(BaseModel):
    listings: List[Listing] = Field(..., description="토지 매물 목록")
    page: int
    size: int
    total: int
