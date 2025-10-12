from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # SQL 쿼리 로그 출력
    pool_pre_ping=True,     # 연결 유효성 체크
    pool_size=10,           # 커넥션 풀 크기
    max_overflow=20,        # 최대 오버플로우 연결 수
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 모델
Base = declarative_base()

# 모든 모델을 레지스트리에 올리기 위한 사이드이펙트 임포트
import app.models  # noqa: F401


def get_db():
    """
    데이터베이스 세션 생성 (의존성 주입용)
    
    Usage:
        @router.get("/")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
