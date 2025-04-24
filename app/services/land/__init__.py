from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.integrations.vworld_api import get_land_feature, get_land_use_plan
from app.utils.convert_code import code2addr
from app.integrations.kakao_api import kakao_get_coord
#import app.functions.model as model
#from app.functions import text_generate

from app.models.land import LandInfo, LandReport
from app.models.user import User, UserFavoriteLand
from app.schemas import land


def _generate_land_data(pnu: str) -> land.Land | None:
    address = code2addr(pnu, dict_format=True)
    lat, lng = kakao_get_coord(address["fulladdr"])
    if not address:
        return None

    year = datetime.now(pytz.timezone("Asia/Seoul")).year
    lf = get_land_feature(pnu, year)
    if not lf:
        return None

    lup = get_land_use_plan(pnu, return2name=True) or "없음"
    detail = land.LandDetail(
        official_price=lf.official_land_price,
        predict_price=None,
        land_cls=lf.cls,
        land_zoning=lf.zoning,
        land_usage=lf.usage,
        register=lf.register,
        area=lf.area,
        height=lf.height,
        form=lf.form,
        road_side=lf.road_side,
        use_plan=lup,
    )
    return land.Land(
        pnu=pnu, address=address, lat=lat, lng=lng, detail=detail,
        last_predict_date=None, land_feature_stdr_year=lf.stdr_year,
        land_trade_list=[], auction=None, listing=None,
    )


def get_land_detail(pnu: str, payload: dict, db: Session) -> dict:
    like = False
    total_like = db.query(UserFavoriteLand).filter_by(pnu=pnu).count()

    if payload:
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")
        like = db.query(UserFavoriteLand).filter_by(user_id=user.user_id, pnu=pnu).first() is not None

    data = get_land_data(pnu, db)
    if not data:
        raise HTTPException(status_code=500, detail="토지 정보를 받아오지 못했습니다.")

    return {
        "status": "success",
        "message": "해당 토지의 정보를 성공적으로 받아왔습니다.",
        "data": data,
        "like": like,
        "total_like": total_like,
    }


def get_land_data(pnu: str, db: Session) -> land.Land | None:
    address = code2addr(pnu, dict_format=True)
    lat, lng = kakao_get_coord(address["fulladdr"])
    if not address:
        return None

    land_info = db.query(LandInfo).filter_by(pnu=pnu).first()
    if land_info:
        detail = land.LandDetail(
            official_price=land_info.official_land_price,
            predict_price=land_info.predict_land_price,
            land_cls=land_info.land_classification,
            land_zoning=land_info.land_zoning,
            land_usage=land_info.land_use_situation,
            register=land_info.land_register,
            area=land_info.land_area,
            height=land_info.land_height,
            form=land_info.land_form,
            road_side=land_info.road_side,
            use_plan=land_info.land_uses,
        )
        return land.Land(
            pnu=pnu, address=address, lat=lat, lng=lng,
            detail=detail, last_predict_date=land_info.predicted_at,
            land_feature_stdr_year=land_info.land_feature_stdr_year,
            land_trade_list=[], auction=None, listing=None,
        )

    new_land = _generate_land_data(pnu)
    if new_land:
        db.add(LandInfo(
            pnu=pnu,
            land_feature_stdr_year=new_land.land_feature_stdr_year,
            official_land_price=new_land.detail.official_price,
            predict_land_price=new_land.detail.predict_price,
            land_classification=new_land.detail.land_cls,
            land_zoning=new_land.detail.land_zoning,
            land_use_situation=new_land.detail.land_usage,
            land_register=new_land.detail.register,
            land_area=new_land.detail.area,
            land_height=new_land.detail.height,
            land_form=new_land.detail.form,
            road_side=new_land.detail.road_side,
            land_uses=new_land.detail.use_plan,
        ))
        db.commit()
        return new_land

    return None


def get_predict_price(pnu: str, db: Session) -> dict:
    land_info = db.query(LandInfo).filter_by(pnu=pnu).first()
    if not land_info:
        raise HTTPException(status_code=404, detail="토지 정보를 찾을 수 없습니다.")

    now = datetime.now(pytz.timezone("Asia/Seoul"))
    # predict_price = str(model.predict(pnu, now.year, now.month))
    # land_info.predict_land_price = predict_price
    # land_info.last_predicted_date = now
    # db.commit()

    # return {
    #     "status": "success",
    #     "message": "해당 토지의 예측가를 성공적으로 받아왔습니다.",
    #     "predict_price": predict_price,
    # }


# def get_land_report(pnu: str, db: Session) -> dict:
#     report_data = db.query(LandReport).filter_by(pnu=pnu).first()
#     if not report_data:
#         report = text_generate.generate(pnu, db)
#         db.add(LandReport(pnu=pnu, report=report))
#         db.commit()
#     else:
#         report = report_data.report

#     return {
#         "status": "success",
#         "message": "토지분석서를 성공적으로 받아왔습니다.",
#         "report": report,
#     }
