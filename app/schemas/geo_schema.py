from typing import Optional, List
from pydantic import BaseModel, Field

from app.dto.geo_dto import AddressDTO


# REQUEST DATA
class GetPNUParams(BaseModel):
    lat: float = Field(..., description="위도 좌표", example=37.5665)
    lng: float = Field(..., description="경도 좌표", example=126.9780)


class GetCoordParams(BaseModel):
    word: Optional[str] = Field(None, description="주소 문자열 (예: 경기도 성남시 분당구 ...)", example="경기도 성남시 분당구")


class AutoCompleteAddressParams(BaseModel):
    query: str = Field(..., description="주소 자동완성용 검색어", example="분당")


class GetCadastralMapParams(BaseModel):
    pnu: List[str] = Field(..., description="토지의 PNU 코드")


# RESPONSE DATA
class GetPNUResponse(BaseModel):
    pnu: str = Field(..., description="19자리 PNU 코드", example="4113511500109350000")
    address: AddressDTO = Field(..., description="해당 PNU에 대한 주소 정보")

class GetCoordResponse(BaseModel):
    lat: float = Field(..., description="위도", example=37.3827531654055)
    lng: float = Field(..., description="경도", example=127.118829944284)
    address: AddressDTO = Field(..., description="지번 주소", example="경기도 성남시 분당구")

class AutoCompleteAddressResponse(BaseModel):
    related_search: List[dict] = Field(
        ...,
        description="자동완성된 주소 검색 결과 목록",
        example=[
            {
                "address": "경기 성남시 분당구 정자동 97-3",
                "road_address": "",
                "lat": "37.370150892237",
                "lng": "127.10613880132"
            },
            {
                "address": "경기 성남시 분당구 야탑동 359-5",
                "road_address": "경기 성남시 분당구 성남대로 919",
                "lat": "37.4118319368872",
                "lng": "127.128210618758"
            },
        ]
    )

class GetCadastralMapResponse(BaseModel):
    polygons: List[List[List[List[List[float]]]]] = Field(
        ...,
        description="지적도 좌표 목록 (다각형)",
        example=[
            [
                [
                    [
                        [
                            126.978,
                            37.5665
                        ],
                        [
                            126.979,
                            37.5665
                        ],
                        [
                            126.979,
                            37.5675
                        ],
                        [
                            126.978,
                            37.5675
                        ],
                        [
                            126.978,
                            37.5665
                        ]
                    ]
                ]
            ]
        ]
    )
