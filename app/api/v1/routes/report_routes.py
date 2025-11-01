# api/v1/routes/report_routes.py
# 아직 리뷰 안끝남
"""
토지 분석 리포트 API
- LLM 기반 토지 분석
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user_optional
from app.services.report_service import ReportService
from app.repositories.report_repository import ReportRepository
from app.repositories.land_repository import LandRepository
from app.schemas.report_schema import LandReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """ReportService 의존성 주입"""
    return ReportService(
        report_repo=ReportRepository(db),
        land_repo=LandRepository(db)
    )


@router.get("/lands/{pnu}", response_model=LandReportResponse)
def get_land_report(
    pnu: str,
    current_user: dict | None = Depends(get_current_user_optional),
    report_service: ReportService = Depends(get_report_service)
):
    """
    토지 분석 리포트 조회/생성
    
    - 기존 리포트가 있으면 반환
    - 없으면 LLM으로 새로 생성 (시간 소요)
    - 로그인 시 조회 이력 저장
    """
    return report_service.get_or_create_report(pnu, current_user)