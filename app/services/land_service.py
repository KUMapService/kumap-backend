from app.dto.land_dto import LandDetailDTO, AddressDTO
from app.repositories.land_repository import LandRepository
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.user_repository import UserRepository
from app.integrations.kakao_api import KakaoAPI
from app.integrations.vworld_api import VWorldAPI
from app.exceptions.land_exceptions import (
    LandNotFoundException,
    LandFeatureNotFoundException,
)
from app.exceptions.user_exceptions import UserNotFoundException
from app.utils.convert_code import code2addr
from app.utils.date import get_now


class LandService:
    """토지 기본 정보 서비스"""
    
    def __init__(
        self,
        land_repo: LandRepository,
        favorite_repo: FavoriteRepository,
        user_repo: UserRepository,
        kakao_api: KakaoAPI | None = None,
        vworld_api: VWorldAPI | None = None
    ):
        self.land_repo = land_repo
        self.favorite_repo = favorite_repo
        self.user_repo = user_repo
        self.kakao_api = kakao_api or KakaoAPI()
        self.vworld_api = vworld_api or VWorldAPI()
    
    def get_land_detail(
        self,
        pnu: str,
        user_email: str | None = None
    ) -> LandDetailDTO:
        """
        토지 상세 정보 조회
        
        Args:
            pnu: PNU 코드
            user_email: 사용자 이메일 (로그인 시)
        
        Returns:
            LandDetailDTO (좋아요 여부 포함)
        """
        # 1. 토지 정보 조회 (없으면 생성)
        land = self.land_repo.find_by_pnu(pnu)
        
        if not land:
            land = self._create_land_from_external_api(pnu)
        
        # 2. 좋아요 여부 확인
        is_liked = False
        if user_email:
            user = self.user_repo.find_by_email(user_email)
            if user:
                is_liked = self.favorite_repo.exists(user.user_id, pnu)

        address = code2addr(pnu, dict_format=True)
        if not address:
            raise LandNotFoundException(pnu)
        
        # 3. DTO 생성
        return LandDetailDTO(
            pnu=land.pnu,
            address=AddressDTO(
                fulladdr=address["fulladdr"],
                sido=address["sido"],
                sigungu=address["sigungu"],
                eupmyeondong=address["eupmyeondong"],
                donglee=address["donglee"],
                detail=address["detail"],
            ),
            lat=land.lat,
            lng=land.lng,
            predicted_price=land.predicted_price,
            last_predicted_date=land.last_predicted_date,
            official_price=land.official_price,
            land_reg=land.land_reg,
            land_cls=land.land_cls,
            land_zoning=land.land_zoning,
            land_usage=land.land_usage,
            land_area=land.land_area,
            land_height=land.land_height,
            land_form=land.land_form,
            road_side=land.road_side,
            use_plan=land.use_plan,
            stdr_year=land.stdr_year,
            stdr_month=land.stdr_month,
            like_count=land.like_count,
            is_liked=is_liked,
        )
    
    def _create_land_from_external_api(self, pnu: str):
        """
        외부 API로부터 토지 정보 생성
        
        VWorld API에서 토지 특성 조회 후 DB에 저장
        """
        # 1. 주소 정보
        address_dict = code2addr(pnu, dict_format=True)
        if not address_dict:
            raise LandNotFoundException(pnu)
        
        # 2. 좌표 조회 (카카오 API)
        lat, lng, _ = self.kakao_api.get_coordinates(address_dict["fulladdr"])
        if not lat or not lng:
            raise LandNotFoundException(pnu)
        
        # 3. 토지 특성 조회 (VWorld API)
        year = get_now().year
        land_feature = self.vworld_api.get_land_feature(pnu, year)
        
        if not land_feature:
            raise LandFeatureNotFoundException(pnu)
        
        # 4. 용도지역 조회
        land_use_plan = self.vworld_api.get_land_use_plan(pnu, use_korean_names=True)
        use_plan = land_use_plan.formatted if land_use_plan else "없음"
        
        # 5. DB에 저장
        land = self.land_repo.create_from_feature(
            pnu=pnu,
            lat=lat,
            lng=lng,
            land_feature=land_feature,
            use_plan=use_plan
        )
        
        return land
    
    def register_owner(self, pnu: str, user_email: str) -> None:
        """토지 소유주 등록"""
        # 토지 존재 확인
        land = self.land_repo.find_by_pnu(pnu)
        if not land:
            raise LandNotFoundException(pnu)
        
        # 사용자 확인
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException(user_email)
        
        # 소유주 등록
        self.land_repo.register_owner(pnu, user.user_id)
    
    def remove_owner(self, pnu: str, user_email: str) -> None:
        """토지 소유주 해제"""
        user = self.user_repo.find_by_email(user_email)
        if not user:
            raise UserNotFoundException(user_email)
        
        self.land_repo.remove_owner(pnu, user.user_id)