
from pydantic import BaseModel, Field, NaiveDatetime

from app.enums.types import Category
from app.dto.auction_dto import AuctionDTO
from app.dto.geo_dto import AddressDTO
from app.dto.listing_dto import ListingDTO


# API DATA SCHEMA
class LandFeature(BaseModel):
    # 토지 특성 정보 데이터 클래스 (공간정보 오픈API 기준)
    pnu: str = Field(..., description="고유번호 (PNU)")
    legal_dong_code: str = Field(..., description="법정동코드")
    legal_dong: str = Field(..., description="법정동명")
    land_reg_code: str = Field(..., description="대장구분코드")
    land_reg: str = Field(..., description="대장구분명")
    land_lot_number: str = Field(..., description="지번")
    stdr_year: str = Field(..., description="기준연도")
    stdr_month: str = Field(..., description="기준월")
    land_cls_code: str = Field(..., description="지목코드")
    land_cls: str = Field(..., description="지목명")
    land_area: float = Field(..., description="토지면적(㎡)")
    land_zoning_code: str = Field(..., description="용도지역코드1")
    land_zoning: str = Field(..., description="용도지역명1")
    land_zoning2_code: str = Field(..., description="용도지역코드2")
    land_zoning2: str = Field(..., description="용도지역명2")
    land_usage_code: str = Field(..., description="토지이용상황코드")
    land_usage: str = Field(..., description="토지이용상황명")
    land_height_code: str = Field(..., description="지형높이코드")
    land_height: str = Field(..., description="지형높이명")
    land_form_code: str = Field(..., description="지형형상코드")
    land_form: str = Field(..., description="지형형상명")
    road_side_code: str = Field(..., description="도로접면코드")
    road_side: str = Field(..., description="도로접면명")
    official_price: float = Field(..., description="공시지가 (원/㎡)")
    last_update_date: str | None = Field(None, description="데이터 기준일자 (YYYY-MM-DD)")

class LandTrade(BaseModel):
    # 토지 매매 정보 데이터 클래스
    pnu: str = Field(..., description="일부 PNU코드")
    address: str = Field(..., description="마스킹된 지번 주소")
    price: float = Field(..., description="거래가격")
    area: float = Field(..., description="거래면적")
    day: int = Field(..., description="거래일자")
    month: int = Field(..., description="거래월")
    year: int = Field(..., description="거래년도")
    cls: str = Field(..., description="지목")
    zoning: str = Field(..., description="용도지역")

class FluctuationRate(BaseModel):
    # 토지 지가변동률 데이터 클래스
    index: float = Field(..., description="지가지수")
    change_rt: float = Field(..., description="지가변동률")
    accumulate_change_rt: float = Field(..., description="누계 지가변동률")

class LandBasicData(BaseModel):
    feature: LandFeature = Field(..., description="")
    uses_plan: str = Field(..., description="")
    uses_plan_code: str = Field(..., description="")
    land_fluctuation_rate: FluctuationRate = Field(..., description="")
    large_cl_fluctuation_rate: FluctuationRate = Field(..., description="")
    ppi: float = Field(..., description="")
    cpi: float = Field(..., description="")
    place_distances: dict = Field(..., description="")
    place_counts_500: dict = Field(..., description="")
    place_counts_1000: dict = Field(..., description="")
    place_counts_3000: dict = Field(..., description="")

    def _return_to_place_data(self) -> str:
        place_data_str = "== 주변 상권 정보 ==\n"
        place_code = Category.place_code()
        for k, v in self.place_distances.items():
            if v != 20000:
                place_data_str += f"{place_code[k]} 최소 거리: {v:,d}m\n"
        for k, v in self.place_counts_500.items():
            if v != 20000:
                place_data_str += f"500m 이내에 있는 {place_code[k]}의 수: {v:,d}개\n"
        for k, v in self.place_counts_1000.items():
            if v != 20000:
                place_data_str += f"1000m 이내에 있는 {place_code[k]}의 수: {v:,d}개\n"
        for k, v in self.place_counts_3000.items():
            if v != 20000:
                place_data_str += f"3000m 이내에 있는 {place_code[k]}의 수: {v:,d}개\n"
        return place_data_str

    def return_to_prompt(self) -> str:
        # 데이터클래스를 프롬프트로 변환하는 함수
        return f"""
        === 토지 정보 ===
        필지: {self.feature.land_reg}
        지목: {self.feature.land_cls}
        용도지역: {self.feature.land_zoning}
        이용상황: {self.feature.land_usage}
        지세: {self.feature.land_height}
        형상: {self.feature.land_form}
        도로접면: {self.feature.road_side}
        이용계획: {self.uses_plan}
        면적: {self.feature.land_area}㎡
        공시지가: {self.feature.official_price}원/㎡
        === 지가변동률 정보 ===
        지가지수: {self.land_fluctuation_rate.index}
        지가변동률: {self.land_fluctuation_rate.change_rt}%
        누계지가변동률: {self.land_fluctuation_rate.accumulate_change_rt}%
        권역별지가지수: {self.large_cl_fluctuation_rate.index}
        권역별지가변동률: {self.large_cl_fluctuation_rate.change_rt}%
        권역별누계지가변동률: {self.large_cl_fluctuation_rate.accumulate_change_rt}%
        === 물가변동률 정보 ===
        생산자물가지수: {self.ppi}
        소비자물가지수: {self.cpi}
        === 주변 상권 정보 ===
        {self._return_to_place_data()}
        """.strip()


# DATA SCHEMA
class LandDetail(BaseModel):
    official_price: float = Field(..., description="공시지가")
    land_reg: str = Field(..., description="필지")
    land_cls: str = Field(..., description="지목")
    land_zoning: str = Field(..., description="용도지역")
    land_usage: str = Field(..., description="이용상황")
    land_area: float = Field(..., description="면적")
    land_height: str = Field(..., description="지세")
    land_form: str = Field(..., description="형상")
    road_side: str = Field(..., description="도로접면")
    use_plan: str = Field(..., description="이용계획")
    stdr_year: str = Field(..., description="기준년도")
    stdr_month: str = Field(..., description="기준월")


# REQUEST DATA
class GetLandRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")


# RESPONSE DATA
class LandDetailResponse(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: AddressDTO = Field(..., description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    predicted_price: float | None = Field(None, description="예측 실거래가")
    last_predicted_date: NaiveDatetime | None = Field(None, description="마지막 토지 가격 예측 일자")
    detail: LandDetail = Field(..., description="토지 특성 정보")
    land_trade_list: list[LandTrade] = Field(..., description="토지 실거래 목록")
    auction: AuctionDTO | None = Field(None, description="경매 정보")
    listing: ListingDTO | None = Field(None, description="매물 정보")
    like_count: int = Field(..., description="토지의 좋아요 개수")
    is_like: bool | None = Field(None, description="사용자의 좋아요 여부")

class LandSimpleData(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: AddressDTO = Field(..., description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    predicted_price: float | None = Field(None, description="예측 실거래가")
    price_ratio: float = Field(..., description="해당 지역의 공시지가 대비 예측가 가격대")
    land_cls: str = Field(..., description="지목")
    land_zoning: str = Field(..., description="용도지역")
    last_predicted_date: NaiveDatetime | None = Field(None, description="마지막 토지 가격 예측 일자")
    like_count: int = Field(..., description="토지의 좋아요 개수")
    is_like: bool | None = Field(False, description="사용자의 좋아요 여부")
    is_auction: bool | None = Field(False, description="토지의 경매 등록 여부")
    is_listing: bool | None = Field(False, description="토지의 매물 등록 여부")

class PredictedPriceResponse(BaseModel):
    predicted_price: float | None = Field(None, description="예측 실거래가")
    last_predicted_date: NaiveDatetime | None = Field(None, description="마지막 토지 가격 예측 일자")

class LandReportResponse(BaseModel):
    pnu: str = Field(..., description="토지 고유 PNU 코드")
    content: str = Field(..., description="생성된 토지 분석서 텍스트")
    like_count: int = Field(..., description="좋아요 수", example=10)
    dislike_count: int = Field(..., description="싫어요 수", example=2)
    generated_at: NaiveDatetime = Field(None, description="리포트 생성 시각 (UTC 기준)")
    is_liked: bool = Field(..., description="현재 사용자가 좋아요를 눌렀는지 여부", example=False)
    is_disliked: bool = Field(..., description="현재 사용자가 싫어요를 눌렀는지 여부", example=False)
