from pydantic import BaseModel, Field
from typing import Optional, List


class AddressDTO(BaseModel):
    """주소 정보 DTO"""
    sido: Optional[str] = Field(None, description="시/도", example="경기도")
    sigungu: Optional[str] = Field(None, description="시/군/구", example="성남시 분당구")
    eupmyeondong: Optional[str] = Field(None, description="읍/면/동", example="운중동")
    donglee: Optional[str] = Field(None, description="동/리 등 세부지역", example="")
    detail: Optional[str] = Field(None, description="상세주소 (해당되는 경우)", example="935")
    fulladdr: Optional[str] = Field(None, description="전체 주소 문자열", example="경기도 성남시 분당구 운중동 935")


class CoordinateDTO(BaseModel):
    """좌표 정보 DTO"""
    lat: float
    lng: float
    address: str
    road_address: str


class PNUCoordinateDTO(BaseModel):
    """PNU와 주소 정보 DTO"""
    pnu: str
    address: AddressDTO


class AddressSuggestion(BaseModel):
    """주소 검색 제안 DTO"""
    address: str
    lat: str
    lng: str
    road_address: str = ""


class CadastralMapDTO(BaseModel):
    """지적도 데이터 DTO"""
    polygons: List[List[List[List[float]]]]
