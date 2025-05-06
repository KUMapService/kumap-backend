from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.enums.response import Status
from app.services.land.geo import geo_service
from app.schemas import APIResponse, error, geo

geo_router = APIRouter(prefix="/geo")


@geo_router.get(
    "/get-pnu", 
    response_model=APIResponse[geo.PNUAddressData], 
    responses=error.make_error_responses(),
    summary="위경도로 PNU 조회", 
    description="위도/경도 값을 기준으로 해당 위치의 PNU 코드와 행정주소를 반환합니다."
)
async def get_pnu(request: geo.GetPNURequest = Depends()):
    pnu, address = geo_service.get_pnu(request)
    return APIResponse[geo.PNUAddressData](
        status="success",
        message="해당 위치의 PNU를 성공적으로 받아왔습니다.",
        data=geo.PNUAddressData(
            pnu=pnu,
            address=address,
        ),
    )

@geo_router.get(
    "/get-coord", 
    response_model=APIResponse[geo.CoordAddressData], 
    responses=error.make_error_responses(),
    summary="주소로 위경도 조회", 
    description="주소 문자열을 기준으로 위도/경도 좌표를 반환합니다. 카카오 API를 사용합니다."
)
async def get_coord(request: geo.GetCoordRequest = Depends()):
    lat, lng = geo_service.get_coord(request)
    return APIResponse[geo.CoordAddressData](
        status="success",
        message="해당 주소의 위경도 데이터를 받아왔습니다.",
        data=geo.CoordAddressData(
            lat=lat,
            lng=lng,
            address=request.word,
        ),
    )

@geo_router.get(
    "/auto-complete-address",
    response_model=APIResponse[geo.AutoCompleteAddressData],
    responses=error.make_error_responses(),
    summary="주소 자동완성 검색",
    description="입력한 문자열을 기반으로 관련된 도로명/지번 주소 후보를 반환합니다.",
)
async def auto_complete_address(request: geo.AutoCompleteAddressRequest = Depends()):
    result = geo_service.auto_complete_address(request)
    return APIResponse[geo.AutoCompleteAddressData](
        status="success",
        message="연관된 도로명/지번 주소를 받아왔습니다.",
        data=geo.AutoCompleteAddressData(
            related_search=result,
        ),
    )

@geo_router.get(
    "/get-cadastral-map",
    response_model=APIResponse[geo.CadastralMapData],
    responses=error.make_error_responses(),
    summary="지적도(Polygon) 데이터 반환",
    description="""
19자리 PNU 코드를 통해 토지의 지적도 데이터를 가져옵니다.  
PNU 코드가 2~8자리일 경우 DB에 저장된 병합 데이터(`multi_polygon`)에서 불러옵니다.  
API 호출 시 최대 10개 이하 권장.
""",
)
async def get_cadastral_map(
    pnu: List[str] = Query(..., description="토지의 PNU 코드"),
    db: Session = Depends(get_db),
):
    polygons = geo_service.get_cadastral_map(pnu, db)
    return APIResponse[geo.CadastralMapData](
        status=Status.SUCCESS,
        message="토지 지적도를 받아왔습니다.",
        data=geo.CadastralMapData(
            polygons=polygons,
        ),
    )

@geo_router.get(
    "/get-address-data",
    response_model=APIResponse[dict],
    summary="시도/시군구/읍면동 데이터 반환",
    description="시도/시군구/읍면동 데이터를 반환합니다."
)
def get_address_data():
    data = geo_service.get_address_data()
    return APIResponse[dict](
        status=Status.SUCCESS,
        message="주소 데이터를 불러왔습니다.",
        data=data,
    )
