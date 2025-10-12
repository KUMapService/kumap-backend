from typing import TypeVar, Generic, Type, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """기본 CRUD 작업을 제공하는 베이스 Repository"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: int) -> ModelType | None:
        """ID로 조회"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, offset: int = 0, limit: int = 100) -> List[ModelType]:
        """전체 목록 조회"""
        return self.db.query(self.model).offset(offset).limit(limit).all()
    
    def create(self, obj: ModelType) -> ModelType:
        """생성"""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def update(self, obj: ModelType) -> ModelType:
        """수정"""
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, obj: ModelType) -> None:
        """삭제"""
        self.db.delete(obj)
        self.db.commit()
    
    def count(self) -> int:
        """총 개수"""
        return self.db.query(self.model).count()
