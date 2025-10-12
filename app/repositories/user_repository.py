from typing import Optional
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """사용자 Repository"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()
    
    def find_by_nickname(self, nickname: str) -> Optional[User]:
        """닉네임으로 사용자 조회"""
        return self.db.query(User).filter(User.nickname == nickname).first()
    
    def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부"""
        return self.db.query(User).filter(User.email == email).count() > 0
    
    def exists_by_nickname(self, nickname: str) -> bool:
        """닉네임 존재 여부"""
        return self.db.query(User).filter(User.nickname == nickname).count() > 0
    
    def update_password(self, user: User, hashed_password: str) -> User:
        """비밀번호 업데이트"""
        user.password = hashed_password
        return self.update(user)
    
    def update_profile(
        self,
        user: User,
        name: Optional[str] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        profile_image_url: Optional[str] = None
    ) -> User:
        """프로필 업데이트"""
        if name is not None:
            user.name = name
        if nickname is not None:
            user.nickname = nickname
        if phone is not None:
            user.phone = phone
        if profile_image_url is not None:
            user.profile_image_url = profile_image_url
        
        return self.update(user)