from pydantic import BaseModel, Field
from typing import List


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
