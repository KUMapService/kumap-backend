from fastapi import HTTPException
from sqlalchemy.orm import Session, aliased

from app.models.land_model import LandListing, LandOwner
from app.models.user_model import User
from app.schemas import listing
from app.utils.convert_code import code2addr


class ListingService:
    """토지 매물 관련 서비스 로직을 처리하는 클래스."""

    def get_listing_data(self, pnu: str, page: int, size: int, payload: dict, db: Session) -> listing.LandListings:
        # 로그인 상태라면 사용자 정보 받아오기
        user_id = None
        if payload:
            email = payload.get("sub")
            user = db.query(User).filter_by(email=email).first()
            if not user:
                raise HTTPException(status_code=404, detail="해당 이메일로 등록된 유저가 없습니다.")
            user_id = user.user_id
        offset = (page - 1) * size
        LandOwnerAlias = aliased(LandOwner)

        datas = (
            db.query(LandListing)
            .join(LandOwnerAlias, LandListing.owner_id == LandOwnerAlias.owner_id)
            .filter(LandOwnerAlias.pnu.like(f"{pnu}%"))
            .offset(offset)
            .limit(size)
            .all()
        )
        total = (
            db.query(LandListing)
            .join(LandOwnerAlias, LandListing.owner_id == LandOwnerAlias.owner_id)
            .filter(LandOwnerAlias.pnu.like(f"{pnu}%"))
            .count()
        )
        # SQLAlchemy 모델을 Pydantic 모델로 변환
        listings = [
            listing.Listing(
                pnu=owner.pnu,
                address=address,
                lat=owner.lat,
                lng=owner.lng,
                area=data.area,
                price=data.price,
                summary=data.summary,
                reg_date=data.registered_at,
                is_my_land=(data.user_id == user_id),
                nickname=data.user.nickname,  # relationship 통해 가져온 유저 닉네임
            )
            for data in datas
            if (owner := data.owner) and (address := code2addr(owner.pnu, dict_format=True))
        ]
        return listing.LandListings(
            listings=listings,
            page=page,
            size=size,
            total=total,
        )

    def get_listing_marker(
        self,
        req: listing.GetListingMarkerRequest,
        db: Session
    ) -> listing.ListingMarker:
        datas = (
            db.query(LandListing, LandOwner)
            .select_from(LandListing)
            .join(LandOwner, LandListing.owner_id == LandOwner.owner_id)
            .filter(
                LandOwner.lat >= req.min_lat,
                LandOwner.lat <= req.max_lat,
                LandOwner.lng >= req.min_lng,
                LandOwner.lng <= req.max_lng
            )
            .all()
        )
        listings = [
            listing.ListingMarker(
                pnu=owner.pnu,
                address=address,
                lat=owner.lat,
                lng=owner.lng,
                area=listing.area,
                price=listing.price,
                reg_date=listing.registered_at,
            )
            for listing, owner in datas
            if (address := code2addr(owner.pnu, dict_format=True)) is not None
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
        # 소유주 등록 여부 확인
        owner = db.query(LandOwner).filter_by(pnu=req.pnu).first()
        if owner is None:
            raise HTTPException(status_code=400, detail="매물 등록 전에 소유주 등록을 먼저 진행해주세요.")
        if owner.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="다른 소유주의 토지는 매물을 등록할 수 없습니다.")
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
        # 소유주 등록 여부 확인
        owner = db.query(LandOwner).filter_by(pnu=pnu).first()
        if owner is None:
            raise HTTPException(status_code=400, detail="소유주 등록이 되어있지 않은 토지입니다.")
        if owner.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="다른 소유주의 토지는 매물을 해제할 수 없습니다.")

        # 매물 제거
        db.delete(listing)
        db.commit()


listing_service = ListingService()
