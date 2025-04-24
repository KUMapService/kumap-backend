from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.land.geo import geo_service
from app.schemas import APIResponse, geo

geo_router = APIRouter(prefix="/geo")


@geo_router.get(
    "/get-pnu", 
    response_model=APIResponse, 
    summary="위경도로 PNU 조회", 
    description="위도/경도 값을 기준으로 해당 위치의 PNU 코드와 행정주소를 반환합니다."
)
async def get_pnu(request: geo.GetPNURequest = Depends()):
    pnu, address = geo_service.get_pnu(request)
    return APIResponse(
        status="success",
        message="해당 위치의 PNU를 성공적으로 받아왔습니다.",
        data=geo.PNUAddressData(
            pnu=pnu,
            address=address,
        ),
    )

@geo_router.get(
    "/get-coord", 
    response_model=APIResponse, 
    summary="주소로 위경도 조회", 
    description="주소 문자열을 기준으로 위도/경도 좌표를 반환합니다. 카카오 API를 사용합니다."
)
async def get_coord(request: geo.GetCoordRequest = Depends()):
    lat, lng = geo_service.get_coord(request)
    return APIResponse(
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
    response_model=APIResponse,
    summary="주소 자동완성 검색",
    description="입력한 문자열을 기반으로 관련된 도로명/지번 주소 후보를 반환합니다.",
)
async def auto_complete_address(request: geo.AutoCompleteAddressRequest = Depends()):
    result = geo_service.auto_complete_address(request)
    return APIResponse(
        status="success",
        message="연관된 도로명/지번 주소를 받아왔습니다.",
        data=geo.AutoCompleteAddressData(
            related_search=result,
        ),
    )

@geo_router.get(
    "/get-cadastral-map",
    response_model=APIResponse,
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
    return APIResponse(
        status="success",
        message="토지 지적도를 받아왔습니다.",
        data=geo.CadastralMapData(
            polygons=polygons,
        ),
    )
