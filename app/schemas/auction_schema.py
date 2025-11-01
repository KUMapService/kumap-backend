from typing import List
from pydantic import BaseModel, Field

from app.dto.auction_dto import AuctionSimpleDTO, AuctionMarkerDTO


# REQUEST DATA
class GetAuctionRequest(BaseModel):
    pnu: str = Field(..., description="PNU 코드 (2자리 or 5자리 or 8자리)")
    page: int = Field(..., description="조회할 페이지")
    size: int = Field(..., description="한 번에 받아올 데이터 크기")

class GetAuctionMarkerRequest(BaseModel):
    min_lat: float = Field(..., description="최소 위도 좌표")
    min_lng: float = Field(..., description="최소 경도 좌표")
    max_lat: float = Field(..., description="최대 위도 좌표")
    max_lng: float = Field(..., description="최대 경도 좌표")

class GetAuctionListRequest(BaseModel):
    pnu_prefix: str = Field(..., description="PNU 코드 (2자리 or 5자리 or 8자리)")
    page: int = Field(..., description="조회할 페이지")
    size: int = Field(..., description="한 번에 받아올 데이터 크기")


# RESPONSE DATA
class AuctionListResponse(BaseModel):
    auctions: List[AuctionSimpleDTO] = Field(..., description="토지 경매 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="한 번에 받아올 데이터 크기")
    total: int = Field(..., description="총 데이터 수")

class AuctionMarkerResponse(BaseModel):
    markers: List[AuctionMarkerDTO] = Field(..., description="토지 경매 마커")
