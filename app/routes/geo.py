from fastapi import APIRouter, Depends, HTTPException, Query
import json
from typing import List
from sqlalchemy.orm import Session
from app import get_db
from app.core.key import VWORLD_API_KEY
from app.functions.api import GetGeometryDataAPI
from app.functions import geo
from app.models.geo import GeometryData
from app.schemas import KUMapBaseResponse, geo

# router
geo_router = APIRouter(prefix="/geo")


@geo_router.get("/get-pnu", response_model=geo.GetPNUResponse)
async def get_pnu(request: geo.GetPNURequest = Depends()):
    try:
        pnu, address = geo.get_pnu(request.lat, request.lng)
        return {
            "status": "success",
            "message": "해당 위치의 PNU를 성공적으로 받아왔습니다.",
            "pnu": pnu,
            "address": address,
            "lat": request.lat,
            "lng": request.lng,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@geo_router.get("/get-coord", response_model=KUMapBaseResponse)
async def get_coord(request: geo.GetCoordRequest = Depends()):
    lat, lng = geo.get_coord(request.word)
    if lat is None or lng is None:
        raise HTTPException(status_code=422, detail="address does not exist")

    return {
        "status": "success",
        "message": "해당 주소의 위경도 데이터를 받아왔습니다.",
        "lat": lat,
        "lng": lng,
        "address": request.word,
    }


@geo_router.get(
    "/auto-complete-address", response_model=geo.AutoCompleteAddressResponse
)
async def auto_complete_address(request: geo.AutoCompleteAddressRequest = Depends()):
    result = geo.auto_complete_address(request.query)

    return {
        "status": "success",
        "message": "해당 주소의 위경도 데이터를 받아왔습니다.",
        "related_search": result,
    }


@geo_router.get("/get-cadastral-map", response_model=geo.GetCadastralMapResponse)
async def get_cadastral_map(
    pnu: List[str] = Query(..., description="Parcel number(s)"),
    db: Session = Depends(get_db),
):
    result = []
    for pnu_code in pnu:
        if len(pnu_code) == 19:
            geo_api = GetGeometryDataAPI(key=VWORLD_API_KEY)
            response = geo_api.get_data(pnu=pnu_code)
            if not response:
                raise HTTPException(
                    status_code=422,
                    detail="해당 토지의 지적도 데이터가 존재하지 않습니다.",
                )
            coordinates = response["features"][0]["geometry"]["coordinates"]
            cleaned_coords = [
                [[float(point[0]), float(point[1])] for point in polygon]
                for polygon in coordinates[0]
            ]
            result.append(cleaned_coords)
        else:
            response = (
                db.query(GeometryData).filter(GeometryData.pnu == pnu_code).first()
            )
            if not response:
                raise HTTPException(
                    status_code=422,
                    detail="해당 토지의 지적도 데이터가 존재하지 않습니다.",
                )
            result.append(json.loads(response.multi_polygon))

    return {
        "status": "success",
        "message": "토지 지적도를 받아왔습니다.",
        "polygons": result,
    }
