from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.land import LandListing
from app.integrations.kakao_api import kakao_get_pnu
from app.schemas import listing


class ListingService:
    """토지 매물 관련 서비스 로직을 처리하는 클래스."""

    def get_listing_data(self, lat: float, lng: float, level: int, payload: dict, db: Session) -> listing.LandListings:
        pnu, _ = kakao_get_pnu(lat, lng)
        if level == 1:
            pnu = pnu[:2]
        else:
            pnu = pnu[:5]
        listings = db.query(LandListing).filter_by(pnu=pnu).all()
        return listing.LandListings(
            listings=listings,
        )
    
    def register_listing(self, req: listing.RegisterListingRequest, db: Session, payload: dict) -> None:
        # 유저 확인
        if not payload:
            raise HTTPException(status_code=401, detail="매물 등록을 하려면 로그인을 해야합니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="해당 이메일로 등록된 유저가 없습니다.")
        # 매물 존재 여부 확인
        listing = db.query(LandListing).filter_by(pnu=req.pnu).first()
        if listing is not None:
            raise HTTPException(status_code=422, detail="해당 토지는 이미 매물로 등록되어 있습니다.")
        # 매물 등록
        db.add(LandListing(
            user_id=user.user_id,
            pnu=req.pnu,
            lat=req.lat,
            lng=req.lng,
            area=req.area,
            price=req.price,
            summary=req.summary,
        ))
        db.commit()
        return
    
    def remove_listing(self, pnu: str, payload: dict, db: Session) -> None:
        # 유저 확인
        if not payload:
            raise HTTPException(status_code=401, detail="매물 등록을 해제하려면 로그인을 해야합니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="해당 이메일로 등록된 유저가 없습니다.")
        # 매물 존재 여부 확인
        listing = db.query(LandListing).filter_by(pnu=pnu).first()
        if not listing:
            raise HTTPException(status_code=422, detail="해당 토지는 매물로 등록되어 있지 않습니다.")
        if listing.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="다른 사람이 올린 매물은 해제할 수 없습니다.")
        # 매물 제거
        db.delete(listing)
        db.commit()





    

listing_service = ListingService()
