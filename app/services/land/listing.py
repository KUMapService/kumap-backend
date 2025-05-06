from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.land import LandListing
from app.schemas import listing
from app.utils.convert_code import code2addr


class ListingService:
    """토지 매물 관련 서비스 로직을 처리하는 클래스."""

    def get_listing_data(self, pnu_prefix: str, page: int, size: int, payload: dict, db: Session) -> listing.LandListings:
        # 로그인 상태라면 사용자 정보 받아오기
        user_id = None
        if payload:
            email = payload.get("sub")
            user = db.query(User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=404, detail="해당 이메일로 등록된 유저가 없습니다.")
            user_id = user.user_id
        offset = (page - 1) * size
        datas = (
            db.query(LandListing)
            .filter(LandListing.pnu.like(f"{pnu_prefix}%"))
            .offset(offset)
            .limit(size)
            .all()
        )
        total = (
            db.query(LandListing)
            .filter(LandListing.pnu.like(f"{pnu_prefix}%"))
            .count()
        )
        # SQLAlchemy 모델을 Pydantic 모델로 변환
        listings = [
            listing.Listing(
                pnu=data.pnu,
                address=address,
                lat=data.lat,
                lng=data.lng,
                area=data.area,
                price=data.price,
                summary=data.summary,
                reg_date=data.registered_at,
                is_my_land=(data.user_id == user_id),
                nickname=data.user.nickname,  # relationship 통해 가져온 유저 닉네임
            )
            for data in datas
            if (address := code2addr(data.pnu, dict_format=True)) is not None
        ]
        return listing.LandListings(
            listings=listings,
            page=page,
            size=size,
            total=total,
        )
    
    def get_listing_marker(self, req: listing.GetListingMarkerRequest, db: Session) -> listing.ListingMarker:
        datas = (
            db.query(LandListing)
            .filter(
                LandListing.lat >= req.min_lat,
                LandListing.lat <= req.max_lat,
                LandListing.lng >= req.min_lng,
                LandListing.lng <= req.max_lng
            )
            .all()
        )
        listings = [
            listing.ListingMarker(
                pnu=data.pnu,
                address=address,
                lat=data.lat,
                lng=data.lng,
                area=data.area,
                price=data.price,
                reg_date=data.registered_at,
            )
            for data in datas
            if (address := code2addr(data.pnu, dict_format=True)) is not None
        ]
        return listings
    
    def register_listing(self, req: listing.RegisterListingRequest,  payload: dict, db: Session) -> None:
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
