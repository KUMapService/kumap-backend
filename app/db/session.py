from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import USER_NAME, USER_PW, DATABASE_NAME

SQLALCHEMY_DATABASE_URL = f"mysql://{USER_NAME}:{USER_PW}@localhost:3306/{DATABASE_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
