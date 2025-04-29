import json
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.integrations.kakao_api import kakao_get_pnu, kakao_get_coord, auto_complete_address
from app.integrations.vworld_api import get_geometry_data
from app.models.geo import GeometryData
from app.schemas import geo


class GeoService:
    def get_pnu(self, request: geo.GetPNURequest):
        pnu, address = kakao_get_pnu(request.lat, request.lng)
        print(pnu, address, flush=True)
        if not pnu or not address:
            raise HTTPException(status_code=500, detail="PNU 정보를 가져오지 못했습니다.")
        return pnu, address

    def get_coord(self, request: geo.GetCoordRequest):
        lat, lng = kakao_get_coord(request.word)
        if lat is None or lng is None:
            raise HTTPException(status_code=422, detail="주소에 해당하는 위경도를 찾을 수 없습니다.")
        return lat, lng

    def auto_complete_address(self, request: geo.AutoCompleteAddressRequest):
        return auto_complete_address(request.query)

    def get_cadastral_map(self, pnu_list: list[str], db: Session):
        result = []
        for pnu_code in pnu_list:
            if len(pnu_code) == 19:
                response = get_geometry_data(pnu=pnu_code)
                if not response:
                    raise HTTPException(status_code=422, detail="해당 토지의 지적도 데이터가 없습니다.")
                coordinates = response["features"][0]["geometry"]["coordinates"]
                cleaned_coords = [
                    [[float(point[0]), float(point[1])] for point in polygon]
                    for polygon in coordinates[0]
                ]
                result.append([cleaned_coords])
            else:
                record = db.query(GeometryData).filter(GeometryData.pnu == pnu_code).first()
                if not record:
                    raise HTTPException(status_code=422, detail="해당 토지의 지적도 데이터가 없습니다.")
                result.append(json.loads(record.multi_polygon))

        return result


geo_service = GeoService()
