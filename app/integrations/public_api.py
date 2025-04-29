import re
import requests
import os
import xmltodict
from typing import Optional, List

from app.core.config import BASE_DIR, LAND_API_KEY
from app.schemas.land import LandTrade
from app.utils.convert_code import code2addr

PNU_CODE_PATH = os.path.join(BASE_DIR, "data", "PnuCode.csv")
_PNU_DICT = None


def _get_pnu_code(sgg_code: str, umd_name: str) -> str:
    global _PNU_DICT
    if _PNU_DICT is not None:
        return _PNU_DICT[sgg_code][umd_name]

    pnu_dict = {}
    with open(PNU_CODE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:
        parts = line.strip().split(",")
        code = parts[0]
        if code[:5] not in pnu_dict.keys():
            pnu_dict[code[:5]] = {}
        umd_dl = " ".join(parts[3:]).strip()
        pnu_dict[code[:5]][umd_dl] = code

    _PNU_DICT = pnu_dict
    return pnu_dict[sgg_code][umd_name]

def get_land_trades(pnu_code: str, year: int, month: int, target_cls: str = None, target_zoning: str = None) -> Optional[List[LandTrade]]:
    """공공데이터포털 API를 사용해 특정 PNU 지역과 월에 해당하는 토지 매매 정보 리스트를 반환합니다."""
    # 1. API 호출
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade"
    params = {
        "serviceKey": LAND_API_KEY,
        "LAWD_CD": pnu_code,
        "DEAL_YMD": f"{year:04d}{month:02d}",
        "numOfRows": "100",
        "pageNo": "1",
    }
    response = requests.get(url, params=params)

    # 2. 응답 파싱
    data = xmltodict.parse(response.text)

    if data["response"]["header"]["resultCode"] != "000":
        return []
    if data["response"]["body"]["totalCount"] == "0":
        return []

    items = data["response"]["body"]["items"]["item"]
    if isinstance(items, dict):
        items = [items]

    # 3. 데이터 가공
    result = []
    for item in items:
        try:
            if "shareDealingType" not in item:
                continue
            if item["shareDealingType"] is None:
                continue
            if target_cls:
                if target_cls != item["jimok"]:
                    continue
            if target_zoning:
                if target_zoning != item["landUse"]:
                    continue
            pnu = _get_pnu_code(item["sggCd"], item["umdNm"])
            if not pnu:
                continue
            masking_address = code2addr(pnu) + " " + item["jibun"]

            jibun = item["jibun"]
            is_san = jibun.startswith("산")
            jibun_num = re.sub(r"\D", "", jibun[1:] if is_san else jibun).zfill(4)

            full_pnu = pnu + ("2" if is_san else "1") + jibun_num

            result.append(LandTrade(
                pnu=full_pnu,
                address=masking_address,
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
    return result
