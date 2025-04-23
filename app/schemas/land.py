from app.schemas import KUMapBaseResponse
from app.schemas.geo import AddressSchema
from pydantic import BaseModel, Field, NaiveDatetime
from typing import Optional, List

# dataclasses
class LandFeature(BaseModel):
    # 토지 특성 정보 데이터 클래스
    pnu: str = Field(..., description="PNU코드")
    register: str = Field(..., description="필지")
    cls: str = Field(..., description="지목")
    zoning: str = Field(..., description="용도지역")
    usage: str = Field(..., description="이용상황")
    height: str = Field(..., description="지세")
    form: str = Field(..., description="형상")
    road_side: str = Field(..., description="도로접면")
    area: float = Field(..., description="면적")
    official_land_price: float = Field(..., description="공시지가")
    stdr_year: str = Field(..., description="기준년도")

class LandTrade(BaseModel):
    # 토지 매매 정보 데이터 클래스
    pnu: str = Field(..., description="일부 PNU코드")
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

class PromptLandData(BaseModel):
    # 프롬프트에 들어가는 토지 데이터 형식
    pnu: str = Field(..., description="PNU코드")
    feature: LandFeature = Field(..., description="토지특성정보")
    uses: str = Field(..., description="토지이용계획")
    land_fluctuation_rate: FluctuationRate = Field(..., description="토지 지가변동률")
    large_cl_fluctuation_rate: FluctuationRate = Field(..., description="권역별 지가변동률")
    ppi: float = Field(..., description="생산자물가지수")
    cpi: float = Field(..., description="소비자물가지수")

    def return_to_prompt(self) -> str:
        # 데이터클래스를 프롬프트로 변환하는 함수
        return f"""
        필지: {self.feature.register}
        지목: {self.feature.cls}
        용도지역: {self.feature.zoning}
        이용상황: {self.feature.usage}
        지세: {self.feature.height}
        형상: {self.feature.form}
        도로접면: {self.feature.road_side}
        이용계획: {self.uses}
        면적: {self.feature.area}㎡
        공시지가: {self.feature.official_land_price}원/㎡
        지가지수: {self.land_fluctuation_rate.index}
        지가변동률: {self.land_fluctuation_rate.change_rt}%
        누계지가변동률: {self.land_fluctuation_rate.accumulate_change_rt}%
        권역별지가지수: {self.large_cl_fluctuation_rate.index}
        권역별지가변동률: {self.large_cl_fluctuation_rate.change_rt}%
        권역별누계지가변동률: {self.large_cl_fluctuation_rate.accumulate_change_rt}%
        생산자물가지수: {self.ppi}
        소비자물가지수: {self.cpi}
        """.strip()

class LandDetail(BaseModel):
    official_price: float = Field(..., description="공시지가")
    predict_price: Optional[float] = Field(None, description="예측 실거래가")
    land_cls: str = Field(..., description="지목")
    land_zoning: str = Field(..., description="용도지역")
    land_usage: str = Field(..., description="이용상황")
    register: str = Field(..., description="필지")
    area: float = Field(..., description="면적")
    height: str = Field(..., description="지세")
    form: str = Field(..., description="형상")
    road_side: str = Field(..., description="도로접면")
    use_plan: str = Field(..., description="이용계획")

class AuctionObj(BaseModel):
    case_cd: str = Field(..., description="사건번호")
    obj_nm: str = Field(..., description="물건번호")
    court_in_charge: str = Field(..., description="담당")
    pnu: str = Field(..., description="PNU코드")
    address: str = Field(..., description="주소")
    summary: str = Field(..., description="설명")


class Auction(BaseModel):
    case_cd: str = Field(..., description="사건번호")
    case_nm: str = Field(..., description="사건번호")
    obj_nm: str = Field(..., description="물건번호")
    case_zoning: str = Field(..., description="감정가")
    appraisal_price: float = Field(..., description="감정가")
    min_price: float = Field(..., description="최저가")
    auction_type: str = Field(..., description="입찰방법")
    auction_date: str = Field(..., description="매각기일")
    court_in_charge: str = Field(..., description="담당")
    court_detail: str = Field(..., description="매각기일")
    case_reception: str = Field(..., description="사건접수")
    auction_start_date: str = Field(..., description="경매개시일")
    div_request_deadline: str = Field(..., description="배당요구종기")
    billable_amount: float = Field(..., description="청구금액")
    date_list: list = Field(..., description="기일내역")
    obj_list: List[AuctionObj] = Field(..., description="물건내역")


class Listing(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    user_id: int = Field(..., description="사용자 ID")
    nickname: str = Field(..., description="사용자 닉네임")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    area: float = Field(..., description="토지 면적")
    price: float = Field(..., description="토지 가격")
    summary: str = Field(..., description="토지 설명")


class Land(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    address: AddressSchema = Field(..., description="주소")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    detail: LandDetail = Field(..., description="토지 특성 정보")
    last_predict_date: Optional[NaiveDatetime] = Field(
        None, description="마지막 토지 가격 예측 일자"
    )
    land_feature_stdr_year: int = Field(..., description="토지 특성 정보 기준년도")
    land_trade_list: list = Field(..., description="토지 실거래 목록")
    auction: Optional[Auction] = Field(None, description="경매 정보")
    listing: Optional[Listing] = Field(None, description="매물 정보")


# requests
class GetLandRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")


# responses
class GetLandDataResponse(KUMapBaseResponse):
    data: Land = Field(..., description="토지 정보 데이터")
    like: bool = Field(..., description="해당 토지의 좋아요 여부")
    total_like: int = Field(..., description="해당 토지의 좋아요 수")

class GetLandPredictedPriceResponse(KUMapBaseResponse):
    predict_price: float = Field(None, description="예측 실거래가")

class GetLandReportResponse(KUMapBaseResponse):
    report: str = Field(..., description="토지분석서 내용")
    