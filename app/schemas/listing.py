from pydantic import BaseModel, Field
from typing import List


# DATA SCHEMA
class Listing(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    user_id: int = Field(..., description="사용자 ID")
    nickname: str = Field(..., description="사용자 닉네임")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    area: float = Field(..., description="토지 면적")
    price: float = Field(..., description="토지 가격")
    summary: str = Field(..., description="토지 설명")
    is_my_land: bool = Field(..., description="사용자 매물 여부")


# REQUEST DATA
class GetListingRequest(BaseModel):
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    level: int = Field(..., description="단위 (1: 시도, 2:시군구)")

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
