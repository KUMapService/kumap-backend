
from typing import Optional, List
from pydantic import BaseModel, Field, NaiveDatetime

from app.dto.geo_dto import AddressDTO


class AuctionMarker(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: Optional[AddressDTO] = Field(None, description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    price: float = Field(..., description="최저가")
    auction_date: NaiveDatetime = Field(..., description="매각기일")


class Auction(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: Optional[AddressDTO] = Field(None, description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    case_cd: str = Field(..., description="사건번호")
    obj_cd: int = Field(..., description="물건번호")
    obj_type: str = Field(..., description="물건종류")
    appraisal_price: float = Field(..., description="감정가")
    min_sale_price: float = Field(..., description="최저가")
    auction_date: NaiveDatetime = Field(..., description="매각기일")
    court_in_charge: str = Field(..., description="담당")
    court_detail: str = Field(..., description="담당부서")
    land_detail: Optional[str] = Field(None, description="세부정보")
    obj_list: List[AuctionMarker] = Field(..., description="물건내역")

class AuctionSimpleData(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: Optional[AddressDTO] = Field(None, description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    case_cd: str = Field(..., description="사건번호")
    obj_cd: int = Field(..., description="물건번호")
    obj_type: str = Field(..., description="물건종류")
    appraisal_price: float = Field(..., description="감정가")
    min_sale_price: float = Field(..., description="최저가")
    auction_date: NaiveDatetime = Field(..., description="매각기일")
    court_in_charge: str = Field(..., description="담당")
    court_detail: str = Field(..., description="담당부서")


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
class LandAuctions(BaseModel):
    auctions: List[AuctionSimpleData] = Field(..., description="토지 경매 목록")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="한 번에 받아올 데이터 크기")
    total: int = Field(..., description="총 데이터 수")
