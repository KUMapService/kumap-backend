from typing import Tuple, Dict, List
from PyKakao import Local

from app.core.config import settings
from app.enums.types import Category
from app.utils.convert_code import code2addr

_local = Local(service_key=settings.KAKAO_API_KEY)


def kakao_get_pnu(lat: float, lng: float) -> Tuple[str, Dict[str, str]]:
    """위도, 경도로부터 PNU 코드 및 주소 정보를 가져온다."""
    try:
        request_address = _local.geo_coord2address(lng, lat, dataframe=False)
        request_region = _local.geo_coord2regioncode(lng, lat, dataframe=False)

        if request_region is None:
            return None, None
        i = 0 if request_region["documents"][0]["region_type"] == "B" else 1
        pnu = request_region["documents"][i]["code"]
        address = request_region["documents"][i]["address_name"]

        if request_address["documents"][i]["address"]["mountain_yn"] == "N":
            mountain = "1"  # 산 X
        else:
            mountain = "2"  # 산 O

        # 본번과 부번의 포멧을 '0000'으로 맞춰줌
        main_no = request_address["documents"][0]["address"]["main_address_no"].zfill(4)
        sub_no = request_address["documents"][0]["address"]["sub_address_no"].zfill(4)
        pnu = str(pnu + mountain + main_no + sub_no)
        address = code2addr(pnu, dict_format=True)

        return pnu, address
    except Exception as e:
        print(e)
        return None, None


def kakao_get_pnu_from_addr(word: str) -> str:
    """주소 문자열로부터 PNU 코드를 가져온다."""
    address = _local.search_address(word, dataframe=False)

    if len(address["documents"]) == 0:
        return None
    pnu = address["documents"][0]["address"]["b_code"]
    pnu = pnu if pnu != "" else address["documents"][0]["address"]["h_code"]
    return pnu


def kakao_get_coord(word: str) -> Tuple[float, float, Dict[str, str], Dict[str, str]]:
    """주소 문자열로부터 (위도, 경도) 좌표를 가져온다."""
    address = _local.search_address(word, dataframe=False)

    if len(address["documents"]) == 0:
        return None, None
    lng = float(address["documents"][0]["x"])
    lat = float(address["documents"][0]["y"])
    address = address["documents"][0]["address"]
    road_address = address["road_address"]
    return lat, lng, address, road_address


def auto_complete_address(query: str) -> List[Dict[str, str]]:
    """주소 자동완성 결과를 가져온다."""
    try:
        response = _local.search_keyword(query, dataframe=False, size=15)["documents"]
        related_search = []
        for r in response:
            related_search.append(
                {
                    "address": r["address_name"],
                    "road_address": r["road_address_name"],
                    "lat": r["y"],
                    "lng": r["x"],
                }
            )
    except:  # noqa: E722
        related_search = []
    return related_search


def get_nearest_place_distance(address: str) -> Dict[str, int]:
    """주소 기준으로 각 카테고리별 가장 가까운 시설 거리(미터)를 가져온다."""
    sa = _local.search_address(address, dataframe=False)
    if not sa["documents"]:
        return None
    x, y = sa["documents"][0]["x"], sa["documents"][0]["y"]
    distances = {}
    for category in Category.list():
        result = _local.search_category(category, x=x, y=y, radius=20000, sort="distance")
        if not result["documents"]:
            distances[category] = 20000
        else:
            distances[category] = int(result["documents"][0]["distance"])
    return distances


def get_place_count_in_radius(address: str, radius: 25) -> Dict[str, int]:
    """주소 기준으로 특정 반경 안에 존재하는 각 카테고리별 시설 개수를 가져온다."""
    sa = _local.search_address(address, dataframe=False)
    if not sa["documents"]:
        return None
    x, y = sa["documents"][0]["x"], sa["documents"][0]["y"]
    counts = {}
    for category in Category.list():
        result = _local.search_category(category, x=x, y=y, radius=radius)
        counts[category] = int(result["meta"]["total_count"])
    return counts
