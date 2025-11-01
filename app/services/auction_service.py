from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.models.land_model import LandAuction
from app.dto.auction_dto import AuctionSimpleDTO, AuctionMarkerDTO
from app.repositories.auction_repository import AuctionRepository
from app.utils.convert_code import code2addr


class AuctionService:
    """토지 경매 서비스"""

    def __init__(self, auction_repo: AuctionRepository):
        """
        토지 경매 서비스 초기화
        
        Args:
            auction_repo: 토지 경매 리포지토리
        """
        self.auction_repo = auction_repo

    def get_auction_list(self, pnu: str, page: int, size: int) -> Tuple[List[AuctionSimpleDTO], int]:
        """
        토지 경매 목록 조회
        
        Args:
            pnu: PNU 코드
            page: 페이지 번호
            size: 페이지 크기
        """
        offset = (page - 1) * size
        data_list, total = self.auction_repo.find_by_pnu_prefix(pnu, offset, size)
        auction_list = [
            AuctionSimpleDTO(
				pnu=data.pnu,
				address=address,
				lat=data.lat,
				lng=data.lng,
				case_cd=data.case_cd,
				obj_cd=data.obj_cd,
				obj_type=data.obj_type,
				appraisal_price=data.appraisal_price,
				min_sale_price=data.min_sale_price,
				auction_date=datetime(
                    year=int(data.auction_date // 10000),
                    month=int((data.auction_date // 100) % 100),
                    day=int(data.auction_date % 100),
                    hour=int(data.auction_time // 100),
                    minute=int(data.auction_time % 100),
                ),
				court_in_charge=data.court_in_charge,
				court_detail=data.court_detail,
            )
            for data in data_list
            if (address := code2addr(data.pnu, dict_format=True)) is not None
        ]
        return auction_list, total

    def get_auction_marker(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> List[AuctionMarkerDTO]:
        """
        토지 경매 마커 조회
        
        Args:
            min_lat: 최소 위도
            min_lng: 최소 경도
            max_lat: 최대 위도
            max_lng: 최대 경도
        """
        data_list = self.auction_repo.find_by_bbox(min_lat, min_lng, max_lat, max_lng)
        auction_marker_list = [
            AuctionMarkerDTO(
                pnu=data.pnu,
                address=address,
                lat=data.lat,
                lng=data.lng,
                price=data.min_sale_price,
				auction_date=datetime(
                    year=int(data.auction_date // 10000),
                    month=int((data.auction_date // 100) % 100),
                    day=int(data.auction_date % 100),
                    hour=int(data.auction_time // 100),
                    minute=int(data.auction_time % 100),
                ),
            )
            for data in data_list
            if (address := code2addr(data.pnu, dict_format=True)) is not None
        ]
        return auction_marker_list
