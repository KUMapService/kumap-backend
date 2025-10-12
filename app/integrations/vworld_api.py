"""
VWorld API 클라이언트
국토교통부 VWorld Open API 래퍼
"""
from typing import Any, Dict, List, Tuple, Optional
from enum import Enum

import requests

from app.core.config import settings
from app.dto.land_dto import (
    LandFeatureDTO,
    FluctuationRateDTO,
    LandUsePlanDTO,
)


class PNULength(int, Enum):
    """PNU 코드 길이"""
    PARCEL = 19  # 필지 (19자리)
    EUPMYEONDONG = 8  # 읍면동 (8자리)
    SIGUNGU = 5  # 시군구 (5자리)
    SIDO = 2  # 시도 (2자리)


class VWorldDataType(str, Enum):
    """VWorld 데이터 타입"""
    PARCEL = "LP_PA_CBND_BUBUN"  # 필지
    EUPMYEONDONG = "LT_C_ADEMD_INFO"  # 읍면동
    SIGUNGU = "LT_C_ADSIGG_INFO"  # 시군구
    SIDO = "LT_C_ADSIDO_INFO"  # 시도


class VWorldAPI:
    """
    VWorld API 클라이언트
    
    국토교통부 VWorld Open API를 사용한 토지 정보 조회
    """
    
    BASE_URL = "https://api.vworld.kr/ned/data"
    MIN_YEAR = 2015         # VWorld API 데이터 제공 최소 연도
    MAX_RETRY_YEARS = 3     # 최대 재시도 연도 수
    DEFAULT_TIMEOUT = 10    # 초
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: VWorld API 키 (기본값: settings에서 로드)
        """
        self.api_key = api_key or settings.VWORLD_API_KEY
    
    def get_land_feature(self, pnu: str, year: int) -> Optional[LandFeatureDTO]:
        """
        토지 특성 정보 조회
        
        Args:
            pnu: PNU 코드 (19자리)
            year: 기준 연도
        
        Returns:
            LandFeatureDTO or None
        
        Example:
            >>> api = VWorldAPI()
            >>> feature = api.get_land_feature("1111011100110880002", 2024)
            >>> print(feature.land_cls)
            '대'
        
        참조:
            https://www.vworld.kr/dtna/dtna_apiSvcFc_s001.do
        """
        # 재귀 깊이 제한을 위한 반복문 사용
        for attempt in range(self.MAX_RETRY_YEARS):
            current_year = year - attempt
            
            if current_year < self.MIN_YEAR:
                return None
            
            data = self._fetch_land_characteristics(pnu, current_year)
            
            if data:
                return self._parse_land_feature(data)
        
        return None
    
    def get_all_region_pnu_codes(self, pnu: str, year: int, max_results: int = 10000) -> List[str]:
        """
        해당 지역의 모든 PNU 코드 조회
        
        Args:
            pnu: 지역 PNU 코드 (2, 5, 8자리)
            year: 기준 연도
            max_results: 최대 결과 수 (기본 10000)
        
        Returns:
            PNU 코드 리스트
        
        Example:
            >>> api = VWorldAPI()
            >>> pnu_list = api.get_all_region_pnu_codes("11110111", 2024)
            >>> len(pnu_list)
            523
        """
        pnu_list = []
        page = 1
        page_size = 1000
        
        while len(pnu_list) < max_results:
            response = self._fetch_land_characteristics_paginated(
                pnu=pnu,
                year=year,
                page=page,
                page_size=page_size
            )
            
            if not response:
                break
            
            data = response.get("data", [])
            total_count = response.get("total_count", 0)
            
            if not data:
                break
            
            # PNU 추출
            for item in data:
                if "pnu" in item:
                    pnu_list.append(item["pnu"])
            
            # 더 이상 데이터가 없으면 중단
            if len(pnu_list) >= total_count:
                break
            
            # 최대 결과 수 도달 시 중단
            if len(pnu_list) >= max_results:
                break
            
            page += 1
            
            # 무한 루프 방지 (최대 100페이지)
            if page > 100:
                break
        
        return pnu_list[:max_results]
    
    def get_land_use_plan(self, pnu: str, use_korean_names: bool = False) -> Optional[LandUsePlanDTO]:
        """
        토지 용도지역 계획 정보 조회
        
        Args:
            pnu: PNU 코드 (19자리)
            use_korean_names: True면 한글명, False면 코드 반환
        
        Returns:
            LandUsePlanDTO or None
        
        Example:
            >>> api = VWorldAPI()
            >>> plan = api.get_land_use_plan("1111011100110880002", use_korean_names=True)
            >>> print(plan.formatted)
            '제2종일반주거지역(지정)/자연녹지지역(지정)'
        """
        try:
            url = f"{self.BASE_URL}/getLandUseAttr"
            params = self._build_common_params(pnu=pnu)
            
            response = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            fields = data.get("landUses", {}).get("field", [])
            if not fields:
                return None
            
            # 용도지역 정보 추출
            plans = []
            for field in fields:
                if use_korean_names:
                    area = field.get("prposAreaDstrcCodeNm", "")
                    conflict = field.get("cnflcAtNm", "")
                else:
                    area = field.get("prposAreaDstrcCode", "")
                    conflict = field.get("cnflcAt", "")
                
                if area:
                    plans.append(f"{area}({conflict})")
            
            # 중복 제거 및 정렬
            unique_plans = sorted(set(plans))
            
            return LandUsePlanDTO(
                plans=unique_plans,
                formatted="/".join(unique_plans)
            )
        
        except requests.RequestException as e:
            print(f"Error fetching land use plan: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_land_use_plan: {e}")
            return None
    
    def get_cadastral_map(self, pnu: str) -> Optional[Dict]:
        """
        지적도 좌표 데이터 조회
        
        Args:
            pnu: PNU 코드 (2, 5, 8, 19자리)
        
        Returns:
            GeoJSON FeatureCollection or None
        """
        # PNU 길이에 따라 데이터 타입 결정
        data_type, attr_filter = self._get_cadastral_map_params(pnu)
        
        if not data_type:
            return None
        
        try:
            url = "http://api.vworld.kr/req/data"
            params = {
                "service": "data",
                "request": "GetFeature",
                "data": data_type,
                "key": self.api_key,
                "attrFilter": attr_filter,
                "page": "1",
                "size": "1000",
            }
            
            response = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            
            # 응답 상태 확인
            if data.get("response", {}).get("status") == "NOT_FOUND":
                return None
            
            return data.get("response", {}).get("result", {}).get("featureCollection")
        
        except requests.RequestException as e:
            print(f"Error fetching geometry data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_geometry: {e}")
            return None
    
    def get_fluctuation_rate_by_region(
        self,
        ld_code: str,
        year: int,
        month: int
    ) -> FluctuationRateDTO | None:
        """
        시군구 기준 월간 땅값 변동률 조회
        
        Args:
            ld_code: 법정동 코드
            year: 연도
            month: 월 (1-12)
        
        Returns:
            FluctuationRateDTO or None
        """
        # 재귀 대신 반복문 사용
        for attempt in range(self.MAX_RETRY_YEARS * 12):  # 최대 36개월
            current_year, current_month = self._adjust_date(year, month, attempt)
            
            if current_year < self.MIN_YEAR:
                return None
            
            try:
                url = f"{self.BASE_URL}/getByRegion"
                params = {
                    **self._build_common_params(),
                    "scopeDiv": "A",
                    "reqLdCode": ld_code,
                    "stdrYear": str(current_year),
                    "stdrMt": f"{current_month:02d}",
                }
                
                response = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                field = data.get("byRegions", {}).get("field", [])
                if field and isinstance(field, list) and len(field) > 0:
                    return self._parse_fluctuation_rate(field[0])
            
            except (requests.RequestException, KeyError, ValueError, TypeError) as e:
                print(f"Error fetching fluctuation rate (attempt {attempt + 1}): {e}")
                continue
        
        return None
    
    def get_fluctuation_rate_by_province(
        self,
        ld_code: str,
        year: int,
        month: int
    ) -> FluctuationRateDTO | None:
        """
        시도 기준 월간 땅값 변동률 조회
        
        Args:
            ld_code: 법정동 코드 (시도 코드는 앞 2자리)
            year: 연도
            month: 월 (1-12)
        
        Returns:
            FluctuationRateDTO or None
        """
        sido_code = ld_code[:2]
        
        for attempt in range(self.MAX_RETRY_YEARS * 12):
            current_year, current_month = self._adjust_date(year, month, attempt)
            
            if current_year < self.MIN_YEAR:
                return None
            
            try:
                url = f"{self.BASE_URL}/getLargeCLByRegion"
                params = {
                    **self._build_common_params(),
                    "scopeDiv": "A",
                    "stdrYear": str(current_year),
                    "stdrMt": f"{current_month:02d}",
                }
                
                response = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                fields = data.get("byRegions", {}).get("field", [])
                
                # 시도 코드 매칭
                for field in fields:
                    if field.get("ldCtprvnCode") == sido_code:
                        return self._parse_fluctuation_rate(field)
            
            except (requests.RequestException, KeyError, ValueError, TypeError) as e:
                print(f"Error fetching province fluctuation rate (attempt {attempt + 1}): {e}")
                continue
        
        return None
    
    def _build_common_params(self, **extra) -> Dict[str, str]:
        """공통 요청 파라미터 생성"""
        params = {
            "key": self.api_key,
            "format": "json",
            "numOfRows": "100",
            "pageNo": "1",
        }
        params.update(extra)
        return params
    
    def _fetch_land_characteristics(self, pnu: str, year: int) -> Optional[Dict[str, Any]]:
        """토지 특성 정보 API 호출"""
        try:
            url = f"{self.BASE_URL}/getLandCharacteristics"
            params = self._build_common_params(pnu=pnu, stdrYear=str(year))
            
            response = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            field = data.get("landCharacteristicss", {}).get("field")
            
            if not field:
                return None
            
            # 리스트면 첫 번째 요소, 아니면 그대로
            return field[0] if isinstance(field, list) else field
        
        except requests.RequestException as e:
            print(f"Error fetching land characteristics: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in _fetch_land_characteristics: {e}")
            return None
    
    def _fetch_land_characteristics_paginated(self, pnu: str, year: int, page: int, page_size: int) -> Optional[Dict[str, Any]]:
        """토지 특성 정보 페이지네이션 조회"""
        try:
            url = f"{self.BASE_URL}/getLandCharacteristics"
            params = {
                "key": self.api_key,
                "format": "json",
                "numOfRows": str(page_size),
                "pageNo": str(page),
                "pnu": pnu,
                "stdrYear": str(year),
            }
            
            response = requests.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            field = data.get("landCharacteristicss", {}).get("field")
            total_count = int(data.get("landCharacteristicss", {}).get("totalCount", 0))
            
            if not field:
                return None
            
            # 리스트가 아니면 리스트로 변환
            if not isinstance(field, list):
                field = [field]
            
            return {
                "data": field,
                "total_count": total_count
            }
        
        except Exception as e:
            print(f"Error in _fetch_land_characteristics_paginated: {e}")
            return None
    
    def _parse_land_feature(self, data: Dict[str, Any]) -> LandFeatureDTO:
        """API 응답을 LandFeatureDTO로 변환"""
        return LandFeatureDTO(
            pnu=data.get("pnu", ""),
            legal_dong_code=data.get("ldCode", ""),
            legal_dong=data.get("ldCodeNm", ""),
            land_reg_code=data.get("regstrSeCode", ""),
            land_reg=data.get("regstrSeCodeNm", ""),
            land_lot_number=data.get("mnnmSlno", ""),
            stdr_year=data.get("stdrYear", ""),
            stdr_month=data.get("stdrMt", ""),
            land_cls_code=data.get("lndcgrCode", ""),
            land_cls=data.get("lndcgrCodeNm", ""),
            land_area=float(data.get("lndpclAr", 0)),
            land_zoning_code=data.get("prposArea1", ""),
            land_zoning=data.get("prposArea1Nm", ""),
            land_zoning2_code=data.get("prposArea2", ""),
            land_zoning2=data.get("prposArea2Nm", ""),
            land_usage_code=data.get("ladUseSittn", ""),
            land_usage=data.get("ladUseSittnNm", ""),
            land_height_code=data.get("tpgrphHgCode", ""),
            land_height=data.get("tpgrphHgCodeNm", ""),
            land_form_code=data.get("tpgrphFrmCode", ""),
            land_form=data.get("tpgrphFrmCodeNm", ""),
            road_side_code=data.get("roadSideCode", ""),
            road_side=data.get("roadSideCodeNm", ""),
            official_price=float(data.get("pblntfPclnd", 0)),
            last_update_date=data.get("lastUpdtDt"),
        )
    
    def _parse_fluctuation_rate(self, field: Dict[str, Any]) -> FluctuationRateDTO:
        """변동률 데이터 파싱"""
        return FluctuationRateDTO(
            index=float(field.get("pclndIndex", 0)),
            change_rt=float(field.get("pclndChgRt", 0)),
            accumulate_change_rt=float(field.get("acmtlPclndChgRt", 0)),
        )
    
    def _get_cadastral_map_params(self, pnu: str) -> Tuple[Optional[str], Optional[str]]:
        """PNU 길이에 따른 geometry 파라미터 결정"""
        pnu_len = len(pnu)
        
        if pnu_len == PNULength.PARCEL:
            return VWorldDataType.PARCEL, f"pnu:=:{pnu}"
        elif pnu_len == PNULength.EUPMYEONDONG:
            return VWorldDataType.EUPMYEONDONG, f"emd_cd:LIKE:{pnu}"
        elif pnu_len == PNULength.SIGUNGU:
            return VWorldDataType.SIGUNGU, f"sig_cd:LIKE:{pnu}"
        elif pnu_len == PNULength.SIDO:
            return VWorldDataType.SIDO, f"ctprvn_cd:LIKE:{pnu}"
        else:
            return None, None
    
    @staticmethod
    def _adjust_date(year: int, month: int, months_back: int) -> Tuple[int, int]:
        """날짜를 N개월 전으로 조정"""
        total_months = year * 12 + month - 1 - months_back
        new_year = total_months // 12
        new_month = total_months % 12 + 1
        return new_year, new_month
