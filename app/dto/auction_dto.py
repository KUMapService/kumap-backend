from typing import Optional, List
from pydantic import BaseModel, Field, NaiveDatetime

from app.dto.geo_dto import AddressDTO


class AuctionMarkerDTO(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: Optional[AddressDTO] = Field(None, description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    price: float = Field(..., description="최저가")
    auction_date: NaiveDatetime = Field(..., description="매각기일")

class AuctionDTO(BaseModel):
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
    obj_list: List[AuctionMarkerDTO] = Field(..., description="물건내역")

class AuctionSimpleDTO(BaseModel):
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
