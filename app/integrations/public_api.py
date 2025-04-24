import re
import requests
import xmltodict
from typing import Optional, List

from app.core.config import LAND_API_KEY
from app.integrations.kakao_api import kakao_get_pnu_from_addr
from app.schemas.land import LandTrade


def get_land_trades(pnu_code: str, year: int, month: int) -> Optional[List[LandTrade]]:
    """공공데이터포털 API를 사용해 특정 PNU 지역과 월에 해당하는 토지 매매 정보 리스트를 반환합니다."""
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
    params = {
        "serviceKey": LAND_API_KEY,
        "LAWD_CD": pnu_code,
        "DEAL_YMD": f"{year:04d}{month:02d}",
        "numOfRows": "100",
        "pageNo": "1",
    }

    response = requests.get(url, params=params)
    data = xmltodict.parse(response.text)

    if data["response"]["header"]["resultCode"] != "000":
        return None
    if data["response"]["body"]["totalCount"] == "0":
        return None

    items = data["response"]["body"]["items"]["item"]
    if isinstance(items, dict):
        items = [items]

    result = []
    for item in items:
        try:
            addr_base = f"{item['estateAgentSggNm']} {item['umdNm']}"
            pnu = kakao_get_pnu_from_addr(addr_base)
            if not pnu:
                continue

            jibun = item["jibun"]
            is_san = jibun.startswith("산")
            jibun_num = re.sub(r"\D", "", jibun[1:] if is_san else jibun).zfill(4)

            full_pnu = pnu + ("2" if is_san else "1") + jibun_num

            result.append(LandTrade(
                pnu=full_pnu,
                price=float(item["dealAmount"].replace(",", "")) * 10000,
                area=float(item["dealArea"]),
                day=int(item["dealDay"]),
                month=int(item["dealMonth"]),
                year=int(item["dealYear"]),
                cls=item["jimok"],
                zoning=item["landUse"],
            ))
        except Exception:
            continue

    return result if result else None
