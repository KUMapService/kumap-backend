import json
import requests
from typing import Optional

from app.core.config import VWORLD_API_KEY
from app.schemas.land import LandFeature, FluctuationRate
from app.utils.date import get_prev_month


def get_land_feature(pnu: str, year: int) -> Optional[LandFeature]:
    """
    PNU와 기준연도를 바탕으로 토지 특성 정보를 가져옴.<br/>
    참조: https://www.vworld.kr/dtna/dtna_apiSvcFc_s001.do
    """
    url = "https://api.vworld.kr/ned/data/getLandCharacteristics"
    params = {
        "key": VWORLD_API_KEY,
        "format": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "pnu": pnu,
        "stdrYear": year,
    }

    response = requests.get(url, params=params).json()
    data = response.get("landCharacteristicss", {}).get("field", None)

    if not data:
        return None if year < 2015 else get_land_feature(pnu, year - 1)

    data = data[0] if isinstance(data, list) else data

    return LandFeature(
        pnu=data["pnu"],
        legal_dong_code=data["ldCode"],
        legal_dong=data["ldCodeNm"],
        land_reg_code=data["regstrSeCode"],
        land_reg=data["regstrSeCodeNm"],
        land_lot_number=data["mnnmSlno"],
        stdr_year=data["stdrYear"],
        stdr_month=data["stdrMt"],
        land_cls_code=data["lndcgrCode"],
        land_cls=data["lndcgrCodeNm"],
        land_area=float(data["lndpclAr"]),
        land_zoning_code=data["prposArea1"],
        land_zoning=data["prposArea1Nm"],
        land_zoning2_code=data["prposArea2"],
        land_zoning2=data["prposArea2Nm"],
        land_usage_code=data["ladUseSittn"],
        land_usage=data["ladUseSittnNm"],
        land_height_code=data["tpgrphHgCode"],
        land_height=data["tpgrphHgCodeNm"],
        land_form_code=data["tpgrphFrmCode"],
        land_form=data["tpgrphFrmCodeNm"],
        road_side_code=data["roadSideCode"],
        road_side=data["roadSideCodeNm"],
        official_price=float(data["pblntfPclnd"]),
        last_update_date=data.get("lastUpdtDt"),
    )

def get_all_region_land_code(pnu: str, year: int) -> Optional[LandFeature]:
    """
    PNU와 기준연도를 바탕으로 해당 지역의 모든 PNU 코드를 가져옴.<br/>
    참조: https://www.vworld.kr/dtna/dtna_apiSvcFc_s001.do
    """
    url = "https://api.vworld.kr/ned/data/getLandCharacteristics"
    
    pnu_list = []
    curr_page = 1
    while True:
        params = {
            "key": VWORLD_API_KEY,
            "format": "json",
            "numOfRows": "1000",
            "pageNo": f"{curr_page}",
            "pnu": pnu,
            "stdrYear": year,
        }
        response = requests.get(url, params=params).json()
        data = response.get("landCharacteristicss", {}).get("field", None)
        total_count = int(response.get("landCharacteristicss", {}).get("totalCount", 0))
        print(total_count)
        if not data:
            return None if year < 2015 else get_land_feature(pnu, year - 1)
        
        for d in data:
            pnu_list.append(d["pnu"])
        if len(pnu_list) < total_count:
            curr_page += 1
        else:
            return pnu_list


def get_land_use_plan(pnu: str, return2name: bool = False) -> Optional[str]:
    """토지의 용도지역 계획 정보를 반환합니다."""
    url = "https://api.vworld.kr/ned/data/getLandUseAttr"
    params = {
        "key": VWORLD_API_KEY,
        "format": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "pnu": pnu,
    }
    response = requests.get(url, params=params).json()
    fields = response.get("landUses", {}).get("field", [])
    if not fields:
        return None

    return "/".join(
        list(set(
            f"{f['prposAreaDstrcCodeNm' if return2name else 'prposAreaDstrcCode']}({f['cnflcAtNm' if return2name else 'cnflcAt']})"
            for f in fields
        ))
    )

def get_geometry_data(pnu: str) -> Optional[dict]:
    """PNU 또는 법정동/시군구/시도 코드 기반으로 지적도 좌표를 반환합니다."""
    if len(pnu) == 19:
        data_type = "LP_PA_CBND_BUBUN"
        attr_filter = f"pnu:=:{pnu}"
    elif len(pnu) == 8:
        data_type = "LT_C_ADEMD_INFO"
        attr_filter = f"emd_cd:LIKE:{pnu}"
    elif len(pnu) == 5:
        data_type = "LT_C_ADSIGG_INFO"
        attr_filter = f"sig_cd:LIKE:{pnu}"
    elif len(pnu) == 2:
        data_type = "LT_C_ADSIDO_INFO"
        attr_filter = f"ctprvn_cd:LIKE:{pnu}"
    else:
        return None

    url = f"http://api.vworld.kr/req/data?service=data&request=GetFeature&data={data_type}&key={VWORLD_API_KEY}&attrFilter={attr_filter}&page=1&size=1000"
    response = json.loads(requests.get(url).text)
    if response["response"]["status"] == "NOT_FOUND":
        return None

    return response["response"]["result"]["featureCollection"]

def get_fluctuation_rate_by_region(ld_code: str, year: int, month: int) -> FluctuationRate | None:
    """시군구 코드 기반 월간 땅값 변동률 데이터 조회"""
    url = "https://api.vworld.kr/ned/data/getByRegion"
    params = {
        "key": VWORLD_API_KEY,
        "format": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "scopeDiv": "A",
        "reqLdCode": ld_code,
        "stdrYear": year,
        "stdrMt": f"{month:02d}",
    }
    response = requests.get(url, params=params).json()
    try:
        field = response["byRegions"]["field"][0]
        return FluctuationRate(
            index=float(field["pclndIndex"]),
            change_rt=float(field["pclndChgRt"]),
            accumulate_change_rt=float(field["acmtlPclndChgRt"]),
        )
    except Exception:
        if year < 2015:
            return None
        new_year, new_month = get_prev_month(year, month)
        return get_fluctuation_rate_by_region(ld_code, new_year, new_month)


def get_fluctuation_rate_by_province(ld_code: str, year: int, month: int) -> FluctuationRate | None:
    """시도 코드 기반 월간 땅값 변동률 데이터 조회"""
    url = "https://api.vworld.kr/ned/data/getLargeCLByRegion"
    params = {
        "key": VWORLD_API_KEY,
        "format": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "scopeDiv": "A",
        "stdrYear": year,
        "stdrMt": f"{month:02d}",
    }
    resp = requests.get(url, params=params).json()
    try:
        for field in resp["byRegions"]["field"]:
            if field["ldCtprvnCode"] == ld_code[:2]:
                return FluctuationRate(
                    index=float(field["pclndIndex"]),
                    change_rt=float(field["pclndChgRt"]),
                    accumulate_change_rt=float(field["acmtlPclndChgRt"]),
                )
    except Exception:
        if year < 2015:
            return None
        new_year, new_month = get_prev_month(year, month)
        return get_fluctuation_rate_by_province(ld_code, new_year, new_month)
