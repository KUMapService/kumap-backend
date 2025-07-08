from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class LandInfo(Base):
    """
    📦 토지 정보 테이블 (LandInfo)

    - PNU 기준으로 각 토지의 특성 정보를 저장
    - 외부 API 기반으로 수집된 공시지가, 용도지역, 지목 등의 데이터를 포함
    - 추후 모델 예측 결과 저장 및 예측일시 기록용으로도 사용
    """

    __tablename__ = "land_info"

    pnu = Column(
        String(20), primary_key=True, 
        comment="필지번호 (PNU)"
    )
    lat = Column(
        Numeric(17, 14), nullable=False,
        comment="위도 (Latitude)"
    )
    lng = Column(
        Numeric(17, 14), nullable=False,
        comment="경도 (Longitude)"
    )
    official_price = Column(
        Float, nullable=False, 
        comment="공시지가 (원)"
    )
    predicted_price = Column(
        Float, nullable=True, 
        comment="예측된 ㅈ토지가격 (원)"
    )
    land_cls = Column(
        String(10), nullable=False, 
        comment="지목 (토지 분류)"
    )
    land_zoning = Column(
        String(20), nullable=False, 
        comment="용도지역"
    )
    land_usage = Column(
        String(20), nullable=False, 
        comment="토지이용 상황"
    )
    land_reg = Column(
        String(10), nullable=False, 
        comment="토지 필지 (일반/산)"
    )
    land_area = Column(
        Float, nullable=False, 
        comment="토지 면적 (㎡)"
    )
    land_height = Column(
        String(10), nullable=False, 
        comment="지형 높이"
    )
    land_form = Column(
        String(10), nullable=False, 
        comment="지형 형태"
    )
    road_side = Column(
        String(10), nullable=False, 
        comment="도로 접면 여부"
    )
    use_plan = Column(
        Text, nullable=True, 
        comment="토지 이용 계획"
    )
    stdr_year = Column(
        String(4), nullable=False, 
        comment="토지특성 기준년도"
    )
    stdr_month = Column(
        String(2), nullable=False, 
        comment="토지특성 기준월"
    )
    last_predicted_date = Column(
        TIMESTAMP, server_default=None, 
        comment="마지막 예측 일시"
    )
    like_count = Column(
        Integer, default=0, nullable=False, 
        comment="좋아요 수"
    )

    def __repr__(self):
        return (
            f"<LandInfo(pnu={self.pnu}, official_price={self.official_price}, "
            f"area={self.land_area}, predicted_price={self.predicted_price})>"
        )

class LandReport(Base):
    """
    📄 토지 리포트 테이블 (LandReport)

    - 토지(PNU)별로 생성된 텍스트 분석 리포트를 저장
    - 사용자 피드백(좋아요/싫어요) 및 생성 시각 포함
    """

    __tablename__ = "land_report"

    report_id = Column(
        Integer, primary_key=True, autoincrement=True,
        comment="분석서 고유 ID"
    )
    pnu = Column(
        String(20), nullable=False,
        comment="PNU 코드 (토지 고유 식별자)"
    )
    content = Column(
        Text, nullable=False,
        comment="생성된 토지 분석서 텍스트"
    )
    like_count = Column(
        Integer, nullable=False, default=0,
        comment="좋아요 수"
    )
    dislike_count = Column(
        Integer, nullable=False, default=0,
        comment="싫어요 수"
    )
    generated_at = Column(
        TIMESTAMP, nullable=True, server_default=func.current_timestamp(),
        comment="리포트 생성 시각"
    )

    def __repr__(self):
        return (
            f"<LandReport(report_id={self.report_id}, pnu='{self.pnu}', "
            f"like_count={self.like_count}, dislike_count={self.dislike_count})>"
        )

class LandTradeHistory(Base):
    """
    💰 토지 실거래 내역 테이블 (LandTradeHistory)

    - 개별 토지(PNU) 기준으로 이뤄진 거래 이력 저장
    - 거래 시점, 가격, 면적, 거래유형 등 포함
    """

    __tablename__ = "land_trade_history"

    trade_id = Column(
        Integer, primary_key=True, autoincrement=True,
        comment="거래 고유 ID"
    )
    pnu = Column(
        String(20), nullable=False,
        comment="PNU 코드 (토지 고유 식별자)"
    )
    land_cls = Column(
        String(10), nullable=False,
        comment="지목 (토지 분류)"
    )
    land_zoning = Column(
        String(20), nullable=False,
        comment="용도지역"
    )
    deal_year = Column(
        Integer, nullable=False,
        comment="거래 연도"
    )
    deal_month = Column(
        Integer, nullable=False,
        comment="거래 월"
    )
    deal_price = Column(
        Float, nullable=False,
        comment="거래 금액 (만원 단위일 가능성 있음)"
    )
    deal_area = Column(
        Float, nullable=False,
        comment="거래 면적 (㎡)"
    )
    deal_type = Column(
        String(10), nullable=True,
        comment="거래 유형 (예: 매매/교환 등)"
    )

    def __repr__(self):
        return (
            f"<LandTradeHistory(trade_id={self.trade_id}, pnu='{self.pnu}', "
            f"deal_year={self.deal_year}, deal_month={self.deal_month}, "
            f"deal_price={self.deal_price})>"
        )

class LandOwner(Base):
    """
    🏠 토지 소유주 테이블 (LandListing)

    - 사용자가 직접 등록한 소유 정보를 저장
    - 등록 시각, 위치 정보, 사용자 등을 포함
    """

    __tablename__ = "land_owner"

    owner_id = Column(
        Integer, primary_key=True, autoincrement=True,
        comment="소유 매물 ID"
    )
    user_id = Column(
        Integer, ForeignKey("user.user_id"), nullable=False, index=True,
        comment="소유주 사용자 ID"
    )
    pnu = Column(
        String(20), nullable=False, index=True,
        comment="PNU 코드 (토지 고유 식별자)"
    )
    lat = Column(
        Numeric(17, 14), nullable=False,
        comment="위도 (Latitude)"
    )
    lng = Column(
        Numeric(17, 14), nullable=False,
        comment="경도 (Longitude)"
    )
    registered_at = Column(
        TIMESTAMP, nullable=True, server_default=func.current_timestamp(),
        comment="등록 시각"
    )

class LandListing(Base):
    """
    🏠 토지 매물 테이블 (LandListing)

    - 사용자가 직접 등록한 매물 정보를 저장
    - 등록 시각, 위치 정보, 요약 설명 등을 포함
    """

    __tablename__ = "land_listing"

    listing_id = Column(
        Integer, primary_key=True, autoincrement=True,
        comment="매물 고유 ID"
    )
    user_id = Column(
        Integer, ForeignKey("user.user_id"), nullable=False, index=True,
        comment="등록한 사용자 ID"
    )
    owner_id = Column(
        Integer, ForeignKey("land_owner.owner_id"), nullable=False,
        comment="등록한 소유 토지 ID"
    )
    area = Column(
        Float, nullable=False,
        comment="면적 (㎡)"
    )
    price = Column(
        Float, nullable=False,
        comment="등록 가격 (단위: 원)"
    )
    summary = Column(
        Text, nullable=False,
        comment="매물 요약 설명"
    )
    registered_at = Column(
        TIMESTAMP, nullable=True, server_default=func.current_timestamp(),
        comment="등록 시각"
    )

    user = relationship(
        "User",
        backref="land_listings",
        lazy="selectin"
    )
    owner = relationship(
        "LandOwner",
        backref="land_listings",
        lazy="selectin"
    )


    def __repr__(self):
        return f"<LandListing(id={self.listing_id}, pnu={self.pnu}, user_id={self.user_id})>"

class LandAuction(Base):
    """
    🏠 토지 경매 테이블 (LandAuction)

    - 법원 경매 사이트에서 크롤링한 정보 중 **토지**만 저장
    - 감정평가액, 최저매각가 등 토지 정보 저장
    """

    __tablename__ = "land_auction"
    
    doc_id = Column(
        String(24), primary_key=True, 
        comment="경매 고유 ID"
    )
    pnu = Column(
        String(20), nullable=False, index=True,
        comment="PNU 코드 (토지 고유 식별자)"
    )
    lat = Column(
        Numeric(17, 14), nullable=False,
        comment="위도 (Latitude)"
    )
    lng = Column(
        Numeric(17, 14), nullable=False,
        comment="경도 (Longitude)"
    )
    case_cd = Column(
        String(15), nullable=False,
        comment="사건번호"
    )
    obj_cd = Column(
        Integer, nullable=False,
        comment="물건번호"
    )
    obj_type = Column(
        String(100), nullable=False,
        comment="물건종류"
    )
    appraisal_price = Column(
        Float, nullable=False,
        comment="감정평가액"
    )
    min_sale_price = Column(
        Float, nullable=False,
        comment="최저입찰가"
    )
    auction_date = Column(
        Integer, nullable=False,
        comment="매각 기일"
    )
    auction_time = Column(
        Integer, nullable=False,
        comment="매각 시간"
    )
    court_in_charge = Column(
        String(20), nullable=False,
        comment="담당법원"
    )
    court_detail = Column(
        String(20), nullable=False,
        comment="담당법원 부서"
    )
    land_detail = Column(
        Text, nullable=True,
        comment="토지 설명"
    )

    def __repr__(self):
        return f"<LandAuction(id={self.doc_id}, pnu={self.pnu})>"
