from fastapi import UploadFile
from passlib.context import CryptContext

from app.dto.user_dto import UserProfileDTO
from app.repositories.user_repository import UserRepository
from app.repositories.land_repository import LandRepository
from app.repositories.listing_repository import ListingRepository
from app.exceptions.user_exceptions import (
    UserNotFoundException,
    InvalidPasswordException,
)
from app.core.config import settings
from app.utils.file_handler import save_profile_image, delete_profile_image


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """사용자 서비스"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        land_repo: LandRepository | None = None,
        listing_repo: ListingRepository | None = None
    ):
        self.user_repo = user_repo
        self.land_repo = land_repo
        self.listing_repo = listing_repo
    
    def get_profile(self, email: str) -> UserProfileDTO:
        """
        사용자 프로필 조회
        
        Args:
            email: 사용자 이메일
        
        Returns:
            UserProfileDTO
        
        Raises:
            UserNotFoundException: 사용자 없음
        """
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise UserNotFoundException()
        
        # 프로필 이미지 URL 생성
        profile_image_url = self._build_profile_image_url(user.profile_image_url)
        
        return UserProfileDTO(
            email=user.email,
            name=user.name,
            nickname=user.nickname,
            phone=user.phone or "",
            phone_verified=user.phone_verified,
            profile_image_url=profile_image_url
        )
    
    def update_profile(
        self,
        email: str,
        name: str,
        nickname: str,
        phone: str,
        is_image_deleted: bool = False,
        image: UploadFile | None = None
    ) -> None:
        """
        프로필 수정
        
        Args:
            email: 사용자 이메일
            name: 이름
            nickname: 닉네임
            phone: 전화번호
            is_image_deleted: 이미지 삭제 여부
            image: 새 프로필 이미지
        
        Raises:
            UserNotFoundException: 사용자 없음
        """
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise UserNotFoundException()
        
        # 기본 정보 업데이트
        user.name = name
        user.nickname = nickname
        user.phone = phone
        
        # 프로필 이미지 처리
        if is_image_deleted:
            # 기존 이미지 삭제
            if user.profile_image_url:
                delete_profile_image(user.profile_image_url)
            user.profile_image_url = None
        
        if image:
            # 기존 이미지 삭제
            if user.profile_image_url:
                delete_profile_image(user.profile_image_url)
            
            # 새 이미지 저장
            image_path = save_profile_image(image, user.user_id)
            user.profile_image_url = image_path
        
        self.user_repo.update(user)
    
    def change_password(
        self,
        email: str,
        current_password: str,
        new_password: str
    ) -> None:
        """
        비밀번호 변경
        
        Args:
            email: 사용자 이메일
            current_password: 현재 비밀번호
            new_password: 새 비밀번호
        
        Raises:
            UserNotFoundException: 사용자 없음
            InvalidPasswordException: 현재 비밀번호 불일치
        """
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise UserNotFoundException()
        
        # 현재 비밀번호 확인
        if not pwd_context.verify(current_password, user.password):
            raise InvalidPasswordException()
        
        # 새 비밀번호 해싱 및 저장
        hashed_password = pwd_context.hash(new_password)
        user.password = hashed_password
        
        self.user_repo.update(user)
    
    def get_owned_lands(self, email: str):
        """소유 토지 목록"""
        # TODO: 구현
        pass
    
    def get_my_listings(self, email: str):
        """등록한 매물 목록"""
        # TODO: 구현
        pass
    
    @staticmethod
    def _build_profile_image_url(profile_image_url: str | None) -> str:
        """
        프로필 이미지 전체 URL 생성
        
        Args:
            profile_image_url: DB에 저장된 이미지 경로
        
        Returns:
            전체 URL
        """
        server_domain = settings.SERVER_DOMAIN
        
        if profile_image_url:
            return f"{server_domain}/static{profile_image_url}"
        else:
            # 기본 이미지
            return f"{server_domain}/static/user/images/default-user-image.png"