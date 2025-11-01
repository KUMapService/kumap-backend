from typing import List

from app.dto.listing_dto import (
    ListingDTO,
    ListingMarkerDTO,
    ListingListResponse,
    CreateListingRequest,
)
from app.repositories.listing_repository import ListingRepository
from app.repositories.owner_repository import OwnerRepository
from app.repositories.user_repository import UserRepository
from app.exceptions.listing_exceptions import (
    ListingAlreadyExistsException,
    ListingNotFoundException,
    NotListingOwnerException,
    OwnerNotRegisteredException,
    NotLandOwnerException,
)
from app.exceptions.user_exceptions import UserNotFoundException
from app.utils.convert_code import code2addr


class ListingService:
    """매물 서비스"""
    
    def __init__(
        self,
        listing_repo: ListingRepository,
        owner_repo: OwnerRepository,
        user_repo: UserRepository
    ):
        self.listing_repo = listing_repo
        self.owner_repo = owner_repo
        self.user_repo = user_repo
    
    def get_listings(
        self,
        pnu_prefix: str,
        page: int,
        size: int,
        user_email: str | None = None
    ) -> ListingListResponse:
        """
        매물 목록 조회
        
        Args:
            pnu_prefix: 지역 PNU (2, 5, 8자리)
            page: 페이지 번호
            size: 페이지 크기
            user_email: 사용자 이메일 (로그인 시)
        
        Returns:
            ListingListResponse
        """
        # 사용자 ID 조회 (로그인한 경우)
        user_id = None
        if user_email:
            user = self.user_repo.find_by_email(user_email)
            if user:
                user_id = user.user_id
        
        # 매물 목록 조회
        skip = (page - 1) * size
        items, total = self.listing_repo.find_by_region_with_owner(
            pnu_prefix=pnu_prefix,
            skip=skip,
            limit=size
        )
        
        # DTO 변환
        listings = []
        for listing, owner in items:
            address = code2addr(owner.pnu, dict_format=True)
            if not address:
                continue
            
            listings.append(ListingDTO(
                pnu=owner.pnu,
                address=address,
                lat=owner.lat,
                lng=owner.lng,
                area=listing.area,
                price=listing.price,
                summary=listing.summary,
                reg_date=listing.registered_at,
                is_my_land=(listing.user_id == user_id),
                nickname=listing.user.nickname,
            ))
        
        return ListingListResponse(
            listings=listings,
            page=page,
            size=size,
            total=total
        )
    
    def get_listing_markers(
        self,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float
    ) -> List[ListingMarkerDTO]:
        """
        지도 영역 내 매물 마커 조회
        
        Args:
            min_lat: 최소 위도
            min_lng: 최소 경도
            max_lat: 최대 위도
            max_lng: 최대 경도
        
        Returns:
            매물 마커 리스트
        """
        items = self.listing_repo.find_by_bbox_with_owner(
            min_lat=min_lat,
            min_lng=min_lng,
            max_lat=max_lat,
            max_lng=max_lng
        )
        
        markers = []
        for listing, owner in items:
            address = code2addr(owner.pnu, dict_format=True)
            if not address:
                continue
            
            markers.append(ListingMarkerDTO(
                pnu=owner.pnu,
                address=address,
                lat=owner.lat,
                lng=owner.lng,
                area=listing.area,
                price=listing.price,
                reg_date=listing.registered_at,
            ))
        
        return markers
    
    def register_listing(
        self,
        request: CreateListingRequest,
        user_email: str
    ) -> None:
        """
        매물 등록
        
        Args:
            request: 매물 등록 요청
            user_email: 사용자 이메일
        
        Raises:
            UserNotFoundException: 사용자 없음
            ListingAlreadyExistsException: 이미 매물 등록됨
            OwnerNotRegisteredException: 소유주 미등록
            NotLandOwnerException: 소유주가 아님
        """
        # 1. 사용자 확인
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException()
        
        # 2. 중복 체크
        if self.listing_repo.exists_by_pnu(request.pnu):
            raise ListingAlreadyExistsException(request.pnu)
        
        # 3. 소유주 확인
        owner = self.owner_repo.find_by_pnu(request.pnu)
        if not owner:
            raise OwnerNotRegisteredException()
        
        # 4. 소유주 권한 확인
        if owner.user_id != user.user_id:
            raise NotLandOwnerException()
        
        # 5. 매물 등록
        self.listing_repo.create_listing(
            user_id=user.user_id,
            owner_id=owner.owner_id,
            pnu=request.pnu,
            lat=request.lat,
            lng=request.lng,
            area=request.area,
            price=request.price,
            summary=request.summary
        )
    
    def remove_listing(self, pnu: str, user_email: str) -> None:
        """
        매물 삭제
        
        Args:
            pnu: PNU 코드
            user_email: 사용자 이메일
        
        Raises:
            UserNotFoundException: 사용자 없음
            ListingNotFoundException: 매물 없음
            NotListingOwnerException: 등록자가 아님
            OwnerNotFoundException: 소유주 없음
            NotLandOwnerException: 소유주가 아님
        """
        # 1. 사용자 확인
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException()
        
        # 2. 매물 확인
        listing = self.listing_repo.find_by_pnu(pnu)
        if not listing:
            raise ListingNotFoundException(pnu)
        
        # 3. 매물 등록자 확인
        if listing.user_id != user.user_id:
            raise NotListingOwnerException()
        
        # 4. 소유주 확인 (이중 체크)
        owner = self.owner_repo.find_by_pnu(pnu)
        if not owner:
            raise OwnerNotFoundException(pnu)
        
        if owner.user_id != user.user_id:
            raise NotLandOwnerException()
        
        # 5. 매물 삭제
        self.listing_repo.delete(listing)
