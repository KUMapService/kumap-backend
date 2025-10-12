from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.enums.response import Status
from app.schemas import APIResponse
from app.schemas.geo_schema import (
    GetPNUParams,
    GetCoordParams,
    AutoCompleteAddressParams,
    GetCadastralMapParams,
    GetPNUResponse,
    GetCoordResponse,
    AutoCompleteAddressResponse,
    GetCadastralMapResponse
)
from app.services.geo_service import GeoService
from app.repositories.geo_repository import GeoRepository

router = APIRouter()


def get_geo_service(db: Session = Depends(get_db)) -> GeoService:
    return GeoService(geo_repo=GeoRepository(db))


@router.get(
    "/coordinates/pnu",
    response_model=APIResponse[GetPNUResponse],
    summary="위경도로 PNU 조회",
    description="위도/경도 값을 기준으로 해당 위치의 PNU 코드와 행정주소를 반환합니다."
)
def get_pnu(
    params: GetPNUParams = Depends(), 
    geo_service: GeoService = Depends(get_geo_service)
):
    result = geo_service.get_pnu_from_coordinates(params.lat, params.lng)
    return APIResponse[GetPNUResponse](
        status=Status.SUCCESS,
        message="해당 위치의 PNU를 성공적으로 받아왔습니다.",
        data=GetPNUResponse(
            pnu=result.pnu,
            address=result.address
        )
    )


@router.get(
    "/addresses/coordinates",
    response_model=APIResponse[GetCoordResponse],
    summary="주소로 위경도 조회",
    description="주소 문자열을 기준으로 위도/경도 좌표를 반환합니다. 카카오 API를 사용합니다."
)
def get_coord(
    params: GetCoordParams = Depends(), 
    geo_service: GeoService = Depends(get_geo_service)
):
    result = geo_service.get_coordinates_from_address(params.word)
    return APIResponse[GetCoordResponse](
        status=Status.SUCCESS,
        message="해당 주소의 위경도 데이터를 받아왔습니다.",
        data=GetCoordResponse(
            lat=result.lat,
            lng=result.lng,
            address=result.address,
            road_address=result.road_address,
        )
    )


@router.get(
    "/auto-complete-address",
    response_model=APIResponse[AutoCompleteAddressResponse],
    summary="주소 자동완성 검색",
    description="입력한 문자열을 기반으로 관련된 도로명/지번 주소 후보를 반환합니다.",
)
def auto_complete_address(
    params: AutoCompleteAddressParams = Depends(), 
    geo_service: GeoService = Depends(get_geo_service)
):
    result = geo_service.auto_complete_address(params.query)
    return APIResponse[AutoCompleteAddressResponse](
        status="success",
        message="연관된 도로명/지번 주소를 받아왔습니다.",
        data=AutoCompleteAddressResponse(
            related_search=result,
        ),
    )

@router.get(
    "/get-cadastral-map",
    response_model=APIResponse[GetCadastralMapResponse],
    summary="지적도(Polygon) 데이터 반환",
    description="""
19자리 PNU 코드를 통해 토지의 지적도 데이터를 가져옵니다.  
PNU 코드가 2~8자리일 경우 DB에 저장된 병합 데이터(`multi_polygon`)에서 불러옵니다.  
API 호출 시 최대 10개 이하 권장.
""",
)
def get_cadastral_map(
    params: GetCadastralMapParams = Depends(),
    geo_service: GeoService = Depends(get_geo_service)
):
    polygons = geo_service.get_cadastral_map(params.pnu)
    return APIResponse[GetCadastralMapResponse](
        status=Status.SUCCESS,
        message="토지 지적도를 받아왔습니다.",
        data=GetCadastralMapResponse(
            polygons=polygons
        )
    )

@router.get(
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
