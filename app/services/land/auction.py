from datetime import datetime
from typing import Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException
from pydantic import NaiveDatetime

from app.enums.types import ReactionType
from app.models.land import LandInfo, LandAuction, LandListing
from app.models.user import User, UserFavoriteLand, UserLandReportReaction
from app.generators.land_prompt import LAND_REPORT_FOR_GUEST
from app.generators.report_generator import generate_land_report
from app.integrations.vworld_api import get_land_feature, get_land_use_plan
from app.integrations.kakao_api import kakao_get_coord
from app.schemas import auction
from app.services.land.predictor import land_price_predictor
from app.utils.convert_code import code2addr
from app.utils.date import get_now

class AuctionService:
	def get_auction_data(self, pnu_prefix: str, page: int, size: int, db: Session) -> auction.LandAuctions:
		offset = (page - 1) * size
		datas = (
            db.query(LandAuction)
            .filter(LandAuction.pnu.like(f"{pnu_prefix}%"))
            .offset(offset)
            .limit(size)
            .all()
        )
		total = (
            db.query(LandAuction)
            .filter(LandAuction.pnu.like(f"{pnu_prefix}%"))
            .count()
        )
        # SQLAlchemy 모델을 Pydantic 모델로 변환
		auctions = [
            auction.AuctionSimpleData(
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
            for data in datas
            if (address := code2addr(data.pnu, dict_format=True)) is not None
        ]
		return auction.LandAuctions(
            auctions=auctions,
            page=page,
            size=size,
            total=total,
        )

	def get_auction_marker(self, req: auction.GetAuctionMarkerRequest, db: Session) -> auction.AuctionMarker:
		datas = (
            db.query(LandAuction)
            .filter(
                LandAuction.lat >= req.min_lat,
                LandAuction.lat <= req.max_lat,
                LandAuction.lng >= req.min_lng,
                LandAuction.lng <= req.max_lng
            )
            .all()
        )
		auctions = [
            auction.AuctionMarker(
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
            for data in datas
            if (address := code2addr(data.pnu, dict_format=True)) is not None
        ]
		return auctions
	

auction_service = AuctionService()