from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.security import JWTBearer
from app.db.session import get_db
from app.enums.response import Status
from app.schemas import APIResponse, error, owner
from app.services.land.owner import owner_service

owner_router = APIRouter(prefix="/owner")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@owner_router.post(
    "",
    response_model=APIResponse,
    summary="토지 소유주 등록",
    description="토지 소유주를 등록합니다."
)
def register_land_owner(
    request: owner.LandOwnerRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    owner_service.register_land_owner(req=request, payload=payload, db=db)
    return APIResponse(
        status=Status.SUCCESS,
        message="해당 토지의 소유주 등록을 완료했습니다.",
    )

@owner_router.delete(
    "",
    response_model=APIResponse,
    responses=error.make_error_responses(need_401=True, need_404=True, need_422=True),
    summary="토지 소유주 제거",
    description="토지 소유주를 제거합니다."
)
def remove_land_owner(
    request: owner.LandOwnerRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db)
):
    owner_service.remove_land_owner(pnu=request.pnu, payload=payload, db=db)
    return APIResponse(
        status=Status.SUCCESS,
        message="해당 토지의 소유주 등록을 해제했습니다.",
    )
