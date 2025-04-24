import requests
from typing import Optional

from app.core.config import ECOS_API_KEY
from app.utils.date import get_prev_month


def get_producer_price_index(year: int, month: int) -> Optional[float]:
    """
    ECOS에서 생산자물가지수(PPI)를 가져옴.

    통계 코드: 404Y014
    항목 코드: *AA (총지수)
    """
    url = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}/json/kr/1/100/"
        f"404Y014/M/{year:04d}{month:02d}/{year:04d}{month:02d}/*AA/?/?/?"
    )
    response = requests.get(url).json()
    if "StatisticSearch" in response:
        return float(response["StatisticSearch"]["row"][0]["DATA_VALUE"])
    if year >= 2015:
        return get_producer_price_index(*get_prev_month(year, month))
    return None

def get_consumer_price_index(year: int, month: int) -> Optional[float]:
    """
    ECOS에서 소비자물가지수(CPI)를 가져옴.

    통계 코드: 901Y009
    항목 코드: 0 (총지수)
    """
    url = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API_KEY}/json/kr/1/100/"
        f"901Y009/M/{year:04d}{month:02d}/{year:04d}{month:02d}/0/?/?/?"
    )
    response = requests.get(url).json()
    if "StatisticSearch" in response:
        return float(response["StatisticSearch"]["row"][0]["DATA_VALUE"])
    if year >= 2015:
        return get_consumer_price_index(*get_prev_month(year, month))
    return None
