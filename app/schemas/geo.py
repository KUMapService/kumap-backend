
from pydantic import BaseModel, Field


# DATA SCHEMA
class AddressSchema(BaseModel):
    sido: str | None = Field(None, description="시/도", example="경기도")
    sigungu: str | None = Field(None, description="시/군/구", example="성남시 분당구")
    eupmyeondong: str | None = Field(None, description="읍/면/동", example="운중동")
    donglee: str | None = Field(None, description="동/리 등 세부지역", example="")
    detail: str | None = Field(None, description="상세주소 (해당되는 경우)", example="935")
    fulladdr: str | None = Field(None, description="전체 주소 문자열", example="경기도 성남시 분당구 운중동 935")


# REQUEST DATA
class GetPNURequest(BaseModel):
    lat: float = Field(..., description="위도 좌표", example=37.5665)
    lng: float = Field(..., description="경도 좌표", example=126.9780)

class GetCoordRequest(BaseModel):
    word: str | None = Field(None, description="주소 문자열 (예: 경기도 성남시 분당구 ...)", example="경기도 성남시 분당구")

class AutoCompleteAddressRequest(BaseModel):
    query: str = Field(..., description="주소 자동완성용 검색어", example="분당")


# RESPONSE DATA
class PNUAddressData(BaseModel):
    pnu: str = Field(..., description="19자리 PNU 코드", example="4113511500109350000")
    address: AddressSchema = Field(..., description="해당 PNU에 대한 주소 정보")

class CoordAddressData(BaseModel):
    lat: float = Field(..., description="위도", example=37.3827531654055)
    lng: float = Field(..., description="경도", example=127.118829944284)
    address: str = Field(..., description="주소 문자열", example="경기도 성남시 분당구")

class AutoCompleteAddressData(BaseModel):
    related_search: list[dict] = Field(
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

class CadastralMapData(BaseModel):
    polygons: list[list[list[list[list[float]]]]] = Field(
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
