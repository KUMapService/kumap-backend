from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.land_model import LandOwner
from app.models.user_model import User
from app.schemas import owner


class OwnerService:
    """토지 소유주 관련 서비스 로직을 처리하는 클래스."""

    def register_land_owner(self, req: owner.LandOwnerRequest,  payload: dict, db: Session) -> None:
        # 유저 확인
        if not payload:
            raise HTTPException(status_code=401, detail="소유주 등록을 하려면 로그인을 해야합니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="해당 이메일로 등록된 유저가 없습니다.")
        # 소유주 존재 여부 확인
        owner = db.query(LandOwner).filter_by(pnu=req.pnu).first()
        if owner is not None:
            raise HTTPException(status_code=422, detail="해당 토지는 이미 소유주가 등록되어 있습니다.")
        # 소유주 등록
        db.add(LandOwner(
            user_id=user.user_id,
            pnu=req.pnu,
            lat=req.lat,
            lng=req.lng,
        ))
        db.commit()
        return

    def remove_land_owner(self, pnu: str, payload: dict, db: Session) -> None:
        # 유저 확인
        if not payload:
            raise HTTPException(status_code=401, detail="소유주 등록을 해제하려면 로그인을 해야합니다.")
        email = payload.get("sub")
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="해당 이메일로 등록된 유저가 없습니다.")
        # 소유주 존재 여부 확인
        owner = db.query(LandOwner).filter_by(pnu=pnu).first()
        if not owner:
            raise HTTPException(status_code=422, detail="해당 토지는 소유주가 등록되어 있지 않습니다.")
        if owner.user_id != user.user_id:
            raise HTTPException(status_code=403, detail="소유주 등록 해제는 본인 소유 토지만 가능합니다.")
        # 소유주 제거
        db.delete(owner)
        db.commit()


owner_service = OwnerService()
