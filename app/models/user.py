from sqlalchemy import Column, SmallInteger, Integer, String, Enum, Boolean, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.enums.types import UserType, ReactionType


class User(Base):
    """
    👤 사용자(User) 테이블

    - 서비스에 가입한 유저들의 기본 정보와 인증 상태를 저장
    - 이메일, 비밀번호, 닉네임 등 주요 로그인 및 식별 정보를 포함
    - 좋아요 테이블(UserFavoriteLand)와 연동됨dg
    """

    __tablename__ = "user"

    user_id = Column(
        Integer, primary_key=True, autoincrement=True, 
        comment="사용자 고유 ID"
    )
    role = Column(
        SmallInteger, nullable=False, server_default=text(str(UserType.GENERAL.value)),
        comment="사용자 역할 (0: 관리자, 1: 일반회원, 2: 유료회원)"
    )
    email = Column(
        String(100), nullable=False, unique=True, 
        comment="사용자 이메일"
    )
    password = Column(
        String(255), nullable=False, 
        comment="사용자 비밀번호"
    )
    name = Column(
        String(20), nullable=False, 
        comment="사용자 이름"
    )
    nickname = Column(
        String(20), nullable=False, unique=True, 
        comment="사용자 닉네임"
    )
    phone = Column(
        String(20), nullable=True, 
        comment="사용자 전화번호"
    )
    phone_verified = Column(
        Boolean, nullable=False, server_default="0", 
        comment="전화번호 인증 여부"
    )
    profile_image_url = Column(
        String(255), nullable=True, 
        comment="프로필 이미지 URL"
    )
    created_at = Column(
        TIMESTAMP, server_default=func.now(), 
        comment="생성일시"
    )
    modified_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), 
        comment="수정일시"
    )
    last_login = Column(
        TIMESTAMP, server_default=func.now(), 
        comment="마지막 로그인 일시"
    )

    favorite_lands = relationship(
        "UserFavoriteLand",
        back_populates="user",
        cascade="all, delete-orphan",  # 유저 삭제되면 좋아요도 같이 삭제
        lazy="selectin",
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, name={self.name})>"

class UserFavoriteLand(Base):
    """
    ⭐ 유저 좋아요(UserFavoriteLand) 테이블

    - 유저가 좋아요한 PNU(토지)의 정보를 저장
    - User 테이블과 외래키(FK)로 연결됨
    """
    
    __tablename__ = "user_favorite_land"

    like_id = Column(
        Integer, primary_key=True, autoincrement=True, 
        comment="좋아요 ID"
    )
    user_id = Column(
        Integer, ForeignKey("user.user_id"), nullable=False, index=True, 
        comment="사용자 ID"
    )
    pnu = Column(
        String(20), nullable=False, index=True, 
        comment="PNU 코드"
    )

    user = relationship(
        "User",
        back_populates="favorite_lands",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<UserFavoriteLand(like_id={self.like_id}, user_id={self.user_id}, pnu={self.pnu})>"

class UserLandReportReaction(Base):
    """
    👍👎 토지 분석서 반응(UserLandReportReaction) 테이블

    - 특정 사용자(User)가 특정 분석서(LandReport)에 남긴 반응 정보 저장
    - 좋아요/싫어요 ReactionType 열거형으로 구분
    """

    __tablename__ = "user_land_report_reaction"

    reaction_id = Column(
        Integer, primary_key=True, autoincrement=True,
        comment="반응 ID"
    )

    user_id = Column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, index=True,
        comment="사용자 ID"
    )

    report_id = Column(
        Integer, ForeignKey("land_report.report_id", ondelete="CASCADE"), nullable=False, index=True,
        comment="분석서 ID"
    )

    reaction_type = Column(
        Enum(ReactionType, name="reaction_type_enum"), nullable=False,
        comment="반응 종류 (like/dislike)"
    )

    created_at = Column(
        TIMESTAMP, server_default=func.now(),
        comment="반응 생성일시"
    )

    # 관계 정의 (optional)
    user = relationship("User", backref="land_report_reactions", lazy="selectin")
    report = relationship("LandReport", backref="user_reactions", lazy="selectin")

    def __repr__(self):
        return f"<UserLandReportReaction(user_id={self.user_id}, report_id={self.report_id}, reaction={self.reaction_type})>"
