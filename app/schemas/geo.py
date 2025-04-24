from pydantic import BaseModel, Field
from typing import Optional, List


# DATA SCHEMA
class AddressSchema(BaseModel):
    sido: Optional[str] = Field(None, description="시/도")
    sigungu: Optional[str] = Field(None, description="시/군/구")
    eupmyeondong: Optional[str] = Field(None, description="읍/면/동")
    donglee: Optional[str] = Field(None, description="동/리 등 세부지역")
    detail: Optional[str] = Field(None, description="상세주소 (해당되는 경우)")
    fulladdr: Optional[str] = Field(None, description="전체 주소 문자열")


# REQUEST DATA
class GetPNURequest(BaseModel):
    lat: float = Field(..., description="위도 좌표")
    lng: float = Field(..., description="경도 좌표")

class GetCoordRequest(BaseModel):
    word: Optional[str] = Field(None, description="주소 문자열 (예: 서울특별시 강남구 ...)")

class AutoCompleteAddressRequest(BaseModel):
    query: str = Field(..., description="주소 자동완성용 검색어")


# RESPONSE DATA
class PNUAddressData(BaseModel):
    pnu: str = Field(..., description="19자리 PNU 코드")
    address: AddressSchema = Field(..., description="해당 PNU에 대한 주소 정보")

class CoordAddressData(BaseModel):
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    address: str = Field(..., description="주소 문자열")

class AutoCompleteAddressData(BaseModel):
    related_search: List[dict] = Field(..., description="자동완성된 주소 검색 결과 목록")

class CadastralMapData(BaseModel):
    polygons: List[List[List[List[List[float]]]]] = Field(..., description="지적도 좌표 목록 (다각형)")
