from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.db.base import Base

class AuctionMarker(Base):
    """
    📍 경매 위치 마커 (위경도 기반)
    """
    __tablename__ = "auction_marker"

    case_cd = Column(
        String(30), primary_key=True, 
        comment="사건번호 (ex. 2024타경12345)"
    )
    lat = Column(
        Numeric(17, 14), nullable=False, 
        comment="위도"
    )
    lng = Column(
        Numeric(17, 14), nullable=False, 
        comment="경도"
    )

    # 관계
    info = relationship("AuctionInfo", back_populates="marker", uselist=False)
    items = relationship("AuctionItem", back_populates="marker")

    def __repr__(self):
        return f"<AuctionMarker(case_cd={self.case_cd}, lat={self.lat}, lng={self.lng})>"

class AuctionInfo(Base):
    """
    📄 경매 사건 정보
    """
    __tablename__ = "auction_info"

    case_cd = Column(
        String(30), ForeignKey("auction_marker.case_cd"), primary_key=True,
        comment="사건번호"
    )
    case_nm = Column(String(100), nullable=False, comment="사건명")
    obj_nm = Column(String(100), nullable=False, comment="물건명")
    case_zoning = Column(String(50), nullable=True, comment="용도지역")
    appraisal_price = Column(Float, nullable=True, comment="감정가")
    min_sale_price = Column(Float, nullable=True, comment="최저매각가격")
    auction_type = Column(String(30), nullable=True, comment="입찰 방식")
    auction_date = Column(String(20), nullable=True, comment="입찰 일자")
    court_in_charge = Column(String(50), nullable=True, comment="담당 법원")
    court_detail = Column(String(100), nullable=True, comment="법원 상세")
    case_reception = Column(String(20), nullable=True, comment="접수일")
    auction_start_date = Column(String(20), nullable=True, comment="입찰개시일")
    div_request_deadline = Column(String(20), nullable=True, comment="배당요구종기일")
    billable_amount = Column(Float, nullable=True, comment="청구금액")
    date_list = Column(Text, nullable=True, comment="입찰 일정 목록 (JSON)")
    land_list = Column(Text, nullable=True, comment="토지 목록 (JSON)")

    marker = relationship("AuctionMarker", back_populates="info")

    def __repr__(self):
        return f"<AuctionInfo(case_cd={self.case_cd}, auction_date={self.auction_date})>"

class AuctionItem(Base):
    """
    📦 경매 물건 정보 (물건 목록)
    """
    __tablename__ = "auction_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_cd = Column(
        String(30), ForeignKey("auction_marker.case_cd"), nullable=False, 
        comment="사건번호"
    )
    obj_nm = Column(String(100), nullable=False, comment="물건명")
    court_in_charge = Column(String(50), nullable=True, comment="담당 법원")
    pnu = Column(String(20), nullable=True, comment="필지 번호 (PNU)")
    addr = Column(String(200), nullable=True, comment="주소")
    detail = Column(Text, nullable=True, comment="물건 상세")

    marker = relationship("AuctionMarker", back_populates="items")

    def __repr__(self):
        return f"<AuctionItem(case_cd={self.case_cd}, obj_nm={self.obj_nm})>"
