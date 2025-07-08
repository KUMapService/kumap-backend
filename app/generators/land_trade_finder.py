# land_trade_finder.py

from app.integrations import public_api
from app.schemas.land import LandBasicData


def find_similar_land_trade(pnu: str, target_cls: str, target_zoning: str, start_year: int, start_month: int) -> LandBasicData | None:
    year, month = start_year, start_month
    trade_land = None
    while True:
        trades = public_api.get_land_trades(pnu_code=pnu[:5], year=year, month=month, target_cls=target_cls, target_zoning=target_zoning)
        #print(trades, flush=True)
        for trade in trades:
            trade_land = trade
            break
        month -= 1
        if month == 0:
            month = 12
            year -= 1
        if year < start_year - 5:
            break
    if trade_land:
        similar_land_str = "=== 비교군 토지 정보 ===\n"
        similar_land_str += f"주소: {trade_land.address}\n"
        similar_land_str += f"거래일자: {trade_land.year}/{trade_land.month}/{trade_land.day}\n"
        similar_land_str += f"거래가격: {trade_land.price}\n"
        similar_land_str += f"거래면적: {trade_land.area}\n"
        similar_land_str += f"지목: {trade_land.cls}\n"
        similar_land_str += f"용도지역: {trade_land.zoning}\n"
        return similar_land_str
    return None
