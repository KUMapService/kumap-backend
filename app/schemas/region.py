from pydantic import BaseModel, Field


# REQUEST DATA
class GetRegionMarkersRequest(BaseModel):
    min_lat: float = Field(..., description="위도 시작 지점", example=37.3827531654055)
    min_lng: float = Field(..., description="경도 시작 지점", example=127.118829944284)
    max_lat: float = Field(..., description="위도 끝 지점", example=37.3927531654055)
    max_lng: float = Field(..., description="경도 끝 지점", example=127.128829944284)
    zoom: int = Field(..., description="지도 확대 레벨", examples=5)

class GetRegionDataRequest(BaseModel):
    pnu: str = Field(..., description="PNU 코드", example="41135105")

class GetRegionLandListRequest(BaseModel):
    pnu: str = Field(..., description="PNU 코드", example="41135105")
    sort_type: int = Field(..., description="정렬 타입 (0: 기본, 1: 높은 가격순, 2: 낮은 가격순, 3: 좋아요순)")
    page: int = Field(..., description="페이지 번호")

# RESPONSE DATA
class RegionData(BaseModel):
    pnu: str = Field(..., description="PNU 코드", example="41135105")
    region: str = Field(..., description="지역명", example="서현동")
    lat: float = Field(..., description="위도", example=37.382810528148)
    lng: float = Field(..., description="경도", example=127.126083586929)
    avg_predict_land_price: float = Field(..., description="해당 지역의 평균 토지 예측가", example=9226708)
    avg_official_price: float = Field(..., description="해당 지역의 평균 공시지가")
    price_ratio: float = Field(..., description="해당 지역의 공시지가 대비 예측가 가격대", example=193.52)
    total_land_count: int = Field(..., description="해당 지역의 토지 수", example=4)

