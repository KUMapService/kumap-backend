import json
from typing import List, Dict

from fastapi import HTTPException

from app.core.config import settings
from app.dto.geo_dto import AddressDTO, CoordinateDTO, PNUCoordinateDTO
from app.exceptions.geo_exceptions import (
    CoordRetrievalError,
    PNURetrievalError,
    CadastralMapNotFoundError
)
from app.integrations.kakao_api import KakaoAPI
from app.integrations.vworld_api import VWorldAPI
from app.repositories.geo_repository import GeoRepository


class GeoService:
    """지적도 관련 서비스"""

    def __init__(self, geo_repo: GeoRepository):
        self.geo_repo = geo_repo
        self.kakao_api = KakaoAPI()
        self.vworld_api = VWorldAPI()
    
    def get_pnu_from_coordinates(self, lat: float, lng: float) -> PNUCoordinateDTO:
        """
        좌표로 PNU 조회
        
        Args:
            lat: 위도
            lng: 경도
        
        Returns:
            PNUCoordinateDTO
        
        Raises:
            PNURetrievalError: PNU 조회 실패
        """
        pnu, address_data = self.kakao_api.get_pnu(lat, lng)

        if not pnu or not address_data:
            raise PNURetrievalError()
        
        address = AddressDTO(**address_data)
        
        return PNUCoordinateDTO(pnu=pnu, address=address)

    def get_coordinates_from_address(self, address: str) -> CoordinateDTO:
        """
        주소로 좌표 조회
        
        Args:
            address: 주소
        
        Returns:
            CoordinateDTO
        
        Raises:
            CoordRetrievalError: 좌표 조회 실패
        """
        lat, lng, address_data = self.kakao_api.get_coordinates(address)

        if lat is None or lng is None:
            raise CoordRetrievalError()
        
        address = AddressDTO(**address_data)
        
        return CoordinateDTO(
            lat=lat, 
            lng=lng, 
            address=address
        )

    def auto_complete_address(self, query: str) -> List[Dict[str, str]]:
        """
        주소 자동완성
        
        Args:
            query: 검색어
        
        Returns:
            List[Dict[str, str]]
        """
        return self.kakao_api.autocomplete_address(query)

    def get_cadastral_map(self, pnu_list: List[str]) -> List[List[List[List[List[float]]]]]:
        result = []
        for pnu_code in pnu_list:
            if len(pnu_code) == 19:
                response = self.vworld_api.get_cadastral_map(pnu=pnu_code)
                if not response:
                    raise CadastralMapNotFoundError(pnu=pnu_code)
                coordinates = response["features"][0]["geometry"]["coordinates"]
                cleaned_coords = [
                    [[float(point[0]), float(point[1])] for point in polygon]
                    for polygon in coordinates[0]
                ]
                result.append([cleaned_coords])
            else:
                record = self.geo_repo.find_geometry_by_pnu(pnu_code)
                if not record:
                    raise CadastralMapNotFoundError(pnu=pnu_code)
                result.append(json.loads(record.multi_polygon))

        return result

    def get_address_data(self):
        f = open(settings.BASE_DIR + "/data/PnuCode.csv", encoding="utf-8")
        lines = f.readlines()
        data = {}
        for line in lines:
            if line.split(",")[1] == "sido":
                continue
            if line.split(",")[1] not in data:
                data[line.split(",")[1]] = {}
            else:
                if line.split(",")[2] != "" and line.split(",")[2] not in data[line.split(",")[1]]:
                    data[line.split(",")[1]][line.split(",")[2]] = []
                else:
                    if line.split(",")[3] != "" and line.split(",")[3] not in data[line.split(",")[1]][line.split(",")[2]]:
                        data[line.split(",")[1]][line.split(",")[2]].append(line.split(",")[3])
        f.close()
        return data
