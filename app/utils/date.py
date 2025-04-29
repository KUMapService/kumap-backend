import pytz
from datetime import datetime


def get_prev_month(year: int, month: int) -> tuple[int, int]:
    """현재 연월에서 전달을 구함. 1월이면 작년 12월 반환."""
    return (year - 1, 12) if month == 1 else (year, month - 1)

def get_now() -> datetime:
    """현재 시간을 timezone-naive 형태로 반환. (기본: Asia/Seoul)"""
    return datetime.now(pytz.timezone("Asia/Seoul")).replace(tzinfo=None)
