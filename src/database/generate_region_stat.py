from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.geo import RegionCoordinate, RegionStat
from app.models.land import LandInfo
from sqlalchemy import func

def update_region_stat(region_obj: RegionCoordinate, db: Session):
    pnu_prefix = region_obj.pnu
    region = region_obj.region

    # 평균 예측 가격
    avg_predicted_price = db.query(func.avg(LandInfo.predicted_price)).filter(
        LandInfo.pnu.like(f"{pnu_prefix}%")
    ).scalar() or 0

    # 유효 필지 개수
    valid_count = db.query(func.count()).filter(
        LandInfo.pnu.like(f"{pnu_prefix}%"),
        LandInfo.predicted_price.isnot(None),
        LandInfo.predicted_price != 0
    ).scalar() or 0

    # 공시지가 평균
    avg_official_price = db.query(func.avg(LandInfo.official_price)).filter(
        LandInfo.pnu.like(f"{pnu_prefix}%")
    ).scalar() or 0

    price_ratio = (avg_predicted_price / avg_official_price * 100) if avg_official_price else 0

    # upsert 처리
    existing = db.query(RegionStat).filter_by(pnu=pnu_prefix).first()
    if existing:
        existing.avg_predicted_price = avg_predicted_price
        existing.price_ratio = price_ratio
        existing.valid_count = valid_count
    else:
        stat = RegionStat(
            pnu=pnu_prefix,
            avg_predicted_price=avg_predicted_price,
            avg_official_price=avg_official_price,
            price_ratio=price_ratio,
            valid_count=valid_count,
        )
        db.add(stat)

    print(f"[STAT] {region} ({pnu_prefix}) 평균가={avg_predicted_price:.2f}, 비율={price_ratio:.2f}%, 유효={valid_count}")

def main():
    db = SessionLocal()
    try:
        regions = db.query(RegionCoordinate).all()
        print(f"총 {len(regions)}개 행정구역 통계 생성 시작")
        for region in regions:
            update_region_stat(region, db)
        db.commit()
        print("[DONE] 지역 통계 캐싱 완료")
    except Exception as e:
        print("[ERROR]", str(e))
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
