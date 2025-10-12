from typing import Tuple, Dict, List, Optional
from enum import Enum
from PyKakao import Local

from app.core.config import settings
from app.enums.types import Category
from app.utils.convert_code import code2addr


class MountainType(str, Enum):
    """산 여부"""
    NORMAL = "1"    # 일반 토지
    MOUNTAIN = "2"  # 산


class RegionType(str, Enum):
    """행정구역 타입"""
    LEGAL = "B"             # 법정동
    ADMINISTRATIVE = "H"    # 행정동


class KakaoAPI:
    """
    카카오맵 API 클라이언트
    
    PyKakao 라이브러리를 사용한 래퍼 클래스
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: 카카오 REST API 키 (기본값: settings에서 로드)
        """
        self._client = Local(service_key=api_key or settings.KAKAO_API_KEY)
        self._max_search_radius = 20000  # 카카오 API 최대 반경 (20km)
    
    def get_pnu(self, lat: float, lng: float) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        """
        좌표로 PNU 코드 및 주소 정보 조회
        
        Args:
            lat: 위도
            lng: 경도
        
        Returns:
            (pnu_code, address_dict) or (None, None)
            - pnu_code: 19자리 PNU 코드
            - address_dict: {sido, sigungu, eupmyeondong, ...}
        """
        try:
            # 주소 정보 조회 (산 여부 확인용)
            coord_address = self._client.geo_coord2address(lng, lat, dataframe=False)
            
            # 행정구역 코드 조회 (법정동 코드 획득용)
            coord_region = self._client.geo_coord2regioncode(lng, lat, dataframe=False)
            
            if not coord_region or not coord_region.get("documents"):
                return None, None
            
            # 법정동 문서 선택
            region_doc = self._select_legal_region(coord_region["documents"])
            if not region_doc:
                return None, None
            
            base_code = region_doc["code"]  # 법정동 코드 (10자리)
            
            # 주소 상세 정보 추출
            if not coord_address or not coord_address.get("documents"):
                return None, None
            
            address_doc = coord_address["documents"][0]["address"]
            
            # PNU 구성 요소 생성
            mountain = self._get_mountain_code(address_doc.get("mountain_yn"))
            main_no = self._format_land_number(address_doc.get("main_address_no", ""))
            sub_no = self._format_land_number(address_doc.get("sub_address_no", ""))
            
            # PNU 생성 (법정동코드(10) + 산여부(1) + 본번(4) + 부번(4) = 19자리)
            pnu = f"{base_code}{mountain}{main_no}{sub_no}"
            
            # PNU로부터 주소 정보 변환
            address_dict = code2addr(pnu, dict_format=True)
            
            return pnu, address_dict
        
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing kakao response in get_pnu: {e}")
            return None, None
        except Exception as e:
            print(f"Unexpected error in get_pnu: {e}")
            return None, None
    
    def get_pnu_from_address(self, address: str) -> Optional[str]:
        """
        주소로 법정동 코드 조회
        
        Args:
            address: 주소 문자열
        
        Returns:
            법정동 코드 (10자리) or None
        """
        try:
            result = self._client.search_address(address, dataframe=False)
            
            if not result or not result.get("documents"):
                return None
            
            addr = result["documents"][0]["address"]
            
            # 법정동 코드 우선, 없으면 행정동 코드
            pnu = addr.get("b_code") or addr.get("h_code")
            
            return pnu if pnu else None
        
        except Exception as e:
            print(f"Error in get_pnu_from_address: {e}")
            return None
    
    def get_coordinates(self, address: str) -> Tuple[Optional[float], Optional[float], Optional[Dict[str, str]]]:
        """
        주소로 좌표 및 주소 정보 조회
        
        Args:
            address: 주소 문자열
        
        Returns:
            (lat, lng, address_dict) or (None, None, None)
        """
        try:
            result = self._client.search_address(address, dataframe=False)
            
            if not result or not result.get("documents"):
                return None, None, None
            
            doc = result["documents"][0]
            print(doc)
            addr = doc["address"]
            
            # 좌표 추출
            lat = float(doc["y"])
            lng = float(doc["x"])
            
            # PNU 생성
            base_code = addr.get("b_code", "")
            if not base_code:
                return lat, lng, None
            
            mountain = self._get_mountain_code(addr.get("mountain_yn"))
            main_no = self._format_land_number(addr.get("main_address_no", ""))
            sub_no = self._format_land_number(addr.get("sub_address_no", ""))
            pnu = f"{base_code}{mountain}{main_no}{sub_no}"

            print(pnu)
            
            # 주소 정보 변환
            address_dict = code2addr(pnu, dict_format=True)
            
            return lat, lng, address_dict
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing response in get_coordinates_with_pnu: {e}")
            return None, None, None
        except Exception as e:
            print(f"Unexpected error in get_coordinates_with_pnu: {e}")
            return None, None, None
    
    def autocomplete_address(self, query: str, size: int = 15) -> List[Dict[str, str]]:
        """
        주소 키워드 검색 (자동완성)
        
        Args:
            query: 검색어
            size: 결과 개수 (기본 15개)
        
        Returns:
            [{"address": str, "road_address": str, "lat": str, "lng": str}, ...]
        """
        try:
            response = self._client.search_keyword(query, dataframe=False, size=size)
            
            if not response or not response.get("documents"):
                return []
            
            results = []
            for doc in response["documents"]:
                results.append({
                    "address": doc.get("address_name", ""),
                    "road_address": doc.get("road_address_name", ""),
                    "lat": doc.get("y", ""),
                    "lng": doc.get("x", ""),
                })
            
            return results
        
        except (KeyError, TypeError) as e:
            print(f"Error parsing response in autocomplete_address: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in autocomplete_address: {e}")
            return []
    
    def get_nearest_place_distances(self, address: str) -> Optional[Dict[str, int]]:
        """
        주소 기준 카테고리별 최근접 시설 거리 조회
        
        Args:
            address: 주소 문자열
        
        Returns:
            {category: distance_in_meters, ...} or None
            - distance는 미터 단위
            - 결과 없으면 20000(20km) 반환
        """
        try:
            # 주소 -> 좌표 변환
            coord_result = self._client.search_address(address, dataframe=False)
            if not coord_result or not coord_result.get("documents"):
                return None
            
            x = coord_result["documents"][0]["x"]
            y = coord_result["documents"][0]["y"]
            
            # 각 카테고리별 최근접 거리 조회
            distances = {}
            
            for category in Category.list():
                category_result = self._client.search_category(
                    category,
                    x=x,
                    y=y,
                    radius=self._max_search_radius,
                    sort="distance"
                )
                
                # 결과가 없으면 최대 거리로 설정
                if not category_result or not category_result.get("documents"):
                    distances[category] = self._max_search_radius
                else:
                    distances[category] = int(category_result["documents"][0]["distance"])
            
            return distances
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error in get_nearest_place_distances: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_nearest_place_distances: {e}")
            return None
    
    def get_place_counts_in_radius(self, address: str, radius: int = 2500) -> Optional[Dict[str, int]]:
        """
        주소 기준 특정 반경 내 카테고리별 시설 개수 조회
        
        Args:
            address: 주소 문자열
            radius: 반경 (미터, 최대 20000)
        
        Returns:
            {category: count, ...} or None
        """
        try:
            # 반경 검증 (카카오 API 최대값)
            radius = min(radius, self._max_search_radius)
            
            # 주소 -> 좌표 변환
            coord_result = self._client.search_address(address, dataframe=False)
            if not coord_result or not coord_result.get("documents"):
                return None
            
            x = coord_result["documents"][0]["x"]
            y = coord_result["documents"][0]["y"]
            
            # 카테고리별 시설 개수 조회
            counts = {}
            
            for category in Category.list():
                category_result = self._client.search_category(
                    category,
                    x=x,
                    y=y,
                    radius=radius
                )
                
                # meta.total_count 추출
                total_count = 0
                if category_result and category_result.get("meta"):
                    total_count = int(category_result["meta"].get("total_count", 0))
                
                counts[category] = total_count
            
            return counts
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error in get_place_counts_in_radius: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_place_counts_in_radius: {e}")
            return None
    
    @staticmethod
    def _select_legal_region(documents: List[Dict]) -> Optional[Dict]:
        """
        법정동(B) 타입 문서 선택
        
        Args:
            documents: 행정구역 정보 문서 리스트
        
        Returns:
            법정동 문서 or 첫 번째 문서 or None
        """
        if not documents:
            return None
        
        # region_type이 "B"(법정동)인 문서 우선 선택
        for doc in documents:
            if doc.get("region_type") == RegionType.LEGAL:
                return doc
        
        # 법정동이 없으면 첫 번째 문서 반환
        return documents[0]
    
    @staticmethod
    def _get_mountain_code(mountain_yn: Optional[str]) -> str:
        """
        산 여부를 코드로 변환
        
        Args:
            mountain_yn: "Y" or "N" or None
        
        Returns:
            "1" (일반) or "2" (산)
        """
        if mountain_yn == "Y":
            return MountainType.MOUNTAIN.value
        return MountainType.NORMAL.value
    
    @staticmethod
    def _format_land_number(number: str) -> str:
        """
        지번을 4자리 포맷으로 변환
        
        Args:
            number: 지번 문자열
        
        Returns:
            4자리 지번 (앞에 0 패딩)
        """
        return (number or "").zfill(4)
