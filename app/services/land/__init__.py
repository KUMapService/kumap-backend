from typing import Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.enums.types import ReactionType
from app.models.land import LandInfo, LandReport
from app.models.user import User, UserFavoriteLand, UserLandReportReaction
from app.generators.report_generator import generate_land_report
from app.integrations.vworld_api import get_land_feature, get_land_use_plan
from app.integrations.kakao_api import kakao_get_coord
from app.schemas import land
from app.services.land.predictor import land_price_predictor
from app.utils.convert_code import code2addr
from app.utils.date import get_now


class LandService:
    """토지 관련 서비스 로직을 처리하는 클래스."""

    def _generate_land_data(self, pnu: str) -> land.LandData:
        address = code2addr(pnu, dict_format=True)
        if not address:
            raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")
        lat, lng = kakao_get_coord(address.fulladdr)
        year = get_now().year
        lf = get_land_feature(pnu, year)
        if not lf:
            raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")
        lup = get_land_use_plan(pnu, return2name=True) or "없음"
        detail = land.LandDetail(
            official_price=lf.official_price,
            land_reg=lf.land_reg,
            land_cls=lf.land_cls,
            land_zoning=lf.land_zoning,
            land_usage=lf.land_usage,
            land_area=lf.land_area,
            land_height=lf.land_height,
            land_form=lf.land_form,
            road_side=lf.road_side,
            use_plan=lup,
            stdr_year=lf.stdr_year,
            stdr_month=lf.stdr_month,
        )
        return land.LandData(
            pnu=pnu, 
            address=address, 
            lat=lat, 
            lng=lng,
            predicted_price=None,
            last_predicted_date=None,
            detail=detail,
            land_trade_list=[], 
            auction=None, 
            listing=None,
            like_count=0,
        )

    def get_land_data(self, pnu: str, db: Session) -> land.LandData:
        address = code2addr(pnu, dict_format=True)
        if not address:
            raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")
        lat, lng = kakao_get_coord(address.fulladdr)
        land_info = db.query(LandInfo).filter_by(pnu=pnu).first()
        # 데이터베이스에 해당 토지에 대한 정보가 있을 경우
        if land_info:
            return land.LandData(
                pnu=pnu,
                address=address,
                lat=lat,
                lng=lng,
                predicted_price=land_info.predicted_price,
                last_predicted_date=land_info.last_predicted_date,
                detail=land.LandDetail(
                    official_price=land_info.official_price,
                    land_reg=land_info.land_reg,
                    land_cls=land_info.land_cls,
                    land_zoning=land_info.land_zoning,
                    land_usage=land_info.land_usage,
                    land_area=land_info.land_area,
                    land_height=land_info.land_height,
                    land_form=land_info.land_form,
                    road_side=land_info.road_side,
                    use_plan=land_info.use_plan,
                    stdr_year=land_info.stdr_year,
                    stdr_month=land_info.stdr_month,
                ),
                land_trade_list=[], 
                auction=None, 
                listing=None,
                like_count=land_info.like_count,
                is_like=False,
            )
        # 데이터베이스에 해당 토지에 대한 정보가 없을 경우
        new_land = self._generate_land_data(pnu)
        if new_land:
            db.add(LandInfo(
                pnu=new_land.pnu,
                official_price=new_land.detail.official_price,
                predicted_price=new_land.predicted_price,
                land_reg=new_land.detail.land_reg,
                land_cls=new_land.detail.land_cls,
                land_zoning=new_land.detail.land_zoning,
                land_usage=new_land.detail.land_usage,
                land_area=new_land.detail.land_area,
                land_height=new_land.detail.land_height,
                land_form=new_land.detail.land_form,
                road_side=new_land.detail.road_side,
                use_plan=new_land.detail.use_plan,
                stdr_year=new_land.detail.stdr_year,
                stdr_month=new_land.detail.stdr_month,
                last_predicted_date=new_land.last_predicted_date,
                like_count=new_land.like_count,
            ))
            db.commit()
            return new_land
        raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")

    def get_land_detail(self, pnu: str, payload: dict, db: Session) -> Tuple[land.LandData, bool]:
        is_like = False
        if payload:
            email = payload.get("sub")
            user = db.query(User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
            is_like = db.query(UserFavoriteLand).filter_by(user_id=user.user_id, pnu=pnu).first() is not None

        data = self.get_land_data(pnu, db)
        if not data:
            raise HTTPException(status_code=500, detail="토지 정보를 받아오지 못했습니다.")
        return data, is_like

    def get_predict_price(self, pnu: str, db: Session) -> land.PredictedPriceData:
        land_info = db.query(LandInfo).filter_by(pnu=pnu).first()
        if not land_info:
            raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")
        now = get_now()
        if land_info.predicted_price is None:
            predicted_data = land_price_predictor.predict(pnu=pnu, year=now.year, month=now.month)
            land_info.predicted_price = predicted_data.predicted_price
            land_info.last_predicted_date = predicted_data.last_predicted_date
            db.commit()
        else:
            predicted_data = land.PredictedPriceData(
                predicted_price=land_info.predicted_price,
                last_predicted_date=land_info.last_predicted_date,
            )
        return predicted_data
    
    def get_land_report(self, pnu: str, payload: dict, db: Session) -> land.LandReportData:
        land_report = db.query(LandReport).filter_by(pnu=pnu).first()
        if not land_report:
            land_info = db.query(LandInfo).filter_by(pnu=pnu).first()
            if not land_info:
                raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")
            if land_info.predicted_price is None:
                raise HTTPException(status_code=404, detail="토지 예측가에 대한 정보를 찾을 수 없습니다.")
            content = generate_land_report(pnu=pnu, predicted_price=land_info.predicted_price)
            land_report = LandReport(
                pnu=pnu,
                content=content,
                like_count=0,
                dislike_count=0,
                generated_at=get_now(),
            )
            db.add(land_report)
            db.commit()
        # 좋아요 여부 확인
        is_liked = False
        is_disliked = False
        if payload:
            email = payload.get("sub")
            user = db.query(User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
            reaction = (
                db.query(UserLandReportReaction)
                .join(LandReport, LandReport.report_id == UserLandReportReaction.report_id)
                .filter(LandReport.pnu == pnu, UserLandReportReaction.user_id == user.user_id)
                .first()
            )
            if reaction:
                if reaction.reaction_type == ReactionType.LIKE:
                    is_liked = True
                elif reaction.reaction_type == ReactionType.DISLIKE:
                    is_disliked = True
        return land.LandReportData(
            pnu=land_report.pnu,
            content=land_report.content,
            like_count=land_report.like_count,
            dislike_count=land_report.dislike_count,
            generated_at=land_report.generated_at,
            is_liked=is_liked,
            is_disliked=is_disliked,
        )


land_service = LandService()
