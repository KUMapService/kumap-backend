import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 디렉토리 경로
    APP_DIR: str
    BASE_DIR: str
    
    # 데이터베이스
    ROOT_PW: str
    DATABASE_NAME: str
    USER_NAME: str
    USER_PW: str
    
    @property
    def DATABASE_URL(self) -> str:
        """SQLAlchemy 데이터베이스 URL 생성"""
        return f"mysql://{self.USER_NAME}:{self.USER_PW}@localhost:3306/{self.DATABASE_NAME}"
    
    # API Keys
    KAKAO_API_KEY: str
    KAKAO_JAVASCRIPT_API_KEY: str
    VWORLD_API_KEY: str
    LAND_API_KEY: str
    ECOS_API_KEY: str
    GOOGLE_API_KEY: str
    
    # SMTP (이메일)
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    
    # 예측 모델
    MODEL_PATH: str
    LLM_MODEL: str
    
    # 서버 설정
    SERVER_PORT: int
    SERVER_DOMAIN: str
    
    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7일
    
    # 추가 설정
    DEBUG: bool = False
    DB_ECHO: bool = False
    
    # CORS
    CORS_ORIGINS: str
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins를 리스트로 반환"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # 파일 업로드
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    # 페이지네이션
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"  # .env에 정의되지 않은 필드도 허용
    )
    
    @property
    def upload_dir(self) -> Path:
        """업로드 디렉토리 경로"""
        return Path(self.APP_DIR) / "static" / "images"
    
    @property
    def model_dir(self) -> Path:
        """모델 디렉토리 경로"""
        return Path(self.MODEL_PATH).parent


# 전역 설정 인스턴스
settings = Settings()


# 환경별 설정 (선택사항)

class DevelopmentSettings(Settings):
    """개발 환경 설정"""
    DEBUG: bool = True
    DB_ECHO: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


class ProductionSettings(Settings):
    """프로덕션 환경 설정"""
    DEBUG: bool = False
    DB_ECHO: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


def get_settings() -> Settings:
    """
    환경에 따른 설정 반환
    
    환경변수 ENVIRONMENT 값에 따라:
    - production: ProductionSettings
    - development (기본): DevelopmentSettings
    """
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# 사용할 설정 선택
# settings = get_settings()  # 환경별 설정 사용 시 이 줄 주석 해제