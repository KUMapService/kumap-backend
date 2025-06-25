import csv
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.config import BASE_DIR
from app.db.session import SessionLocal
from app.models.land import LandInfo
from app.services.land import LandService
from app.integrations.vworld_api import get_all_region_land_code

PNU_CODE_PATH = os.path.join(BASE_DIR, "data", "PnuCode.csv")
MAX_LAND_PER_REGION = 10

land_service = LandService()

def insert_land_data(pnu: str, db: Session):
    try:
        # 기존 데이터 있는지 체크
        exists = db.query(LandInfo).filter_by(pnu=pnu).first()
        if exists:
            print(f"[SKIP] {pnu} already exists")
            return

        # 토지 데이터 생성
        land_data = land_service._generate_land_data(pnu)
        land_info = LandInfo(
            pnu=pnu,
            official_price=land_data.detail.official_price,
            predicted_price=None,
            land_cls=land_data.detail.land_cls,
            land_zoning=land_data.detail.land_zoning,
            land_usage=land_data.detail.land_usage,
            land_reg=land_data.detail.land_reg,
            land_area=land_data.detail.land_area,
            land_height=land_data.detail.land_height,
            land_form=land_data.detail.land_form,
            road_side=land_data.detail.road_side,
            use_plan=land_data.detail.use_plan,
            stdr_year=land_data.detail.stdr_year,
            stdr_month=land_data.detail.stdr_month,
        )

        db.add(land_info)
        db.commit()
        
        # 예측 가격도 바로 생성
        land_service.get_predict_price(pnu=pnu, db=db)
        
        print(f"[INSERT] {pnu} {land_data.address.fulladdr}")
    except HTTPException as e:
        print(f"[ERROR] {pnu}: {e.detail}")
    except Exception as e:
        print(f"[EXCEPTION] {pnu}: {e}")


def main():
    db: Session = SessionLocal()
    with open(PNU_CODE_PATH, encoding="utf-8") as f:
        csv_mapping = list(csv.DictReader(f))

    for data in csv_mapping:
        pnu_prefix = data["code"]
        count = 0
        print(f"[REGION] {pnu_prefix} - {data['sido']} {data['sigungu']} {data['eupmyeondong']} {data['donglee']}")

        pnu_list = get_all_region_land_code(pnu_prefix, 2024)
        if not pnu_list:
            continue

        for pnu in pnu_list:
            insert_land_data(pnu, db)
            count += 1
            if count >= MAX_LAND_PER_REGION:
                break

    db.close()


if __name__ == "__main__":
    main()
