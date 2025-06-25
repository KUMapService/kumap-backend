import csv
import os
from typing import Union
from functools import lru_cache

from app.core.config import BASE_DIR
from app.schemas.geo import AddressSchema

PNU_CODE_PATH = os.path.join(BASE_DIR, "data", "PnuCode.csv")


@lru_cache(maxsize=1)
def load_pnu_mapping():
    with open(PNU_CODE_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def code2addr(code: str, scale: int = 0, dict_format: bool = False) -> Union[str, AddressSchema, None]:
    """PNU 코드를 주소로 변환"""
    csv_mapping = load_pnu_mapping()  # 캐시된 데이터 사용
    match = next((d for d in csv_mapping if d["code"].startswith(code[:10])), None)
    if not match:
        return None

    sido, sigungu, eupmyeondong, donglee = (
        match["sido"],
        match["sigungu"],
        match["eupmyeondong"],
        match.get("donglee", "")
    )

    detail = None
    m = ""
    if len(code) == 19:
        m = "" if code[10] == "1" else "산"
        main_n = int(code[11:15])
        sub_n = int(code[15:19])
        detail = f"{main_n}-{sub_n}" if sub_n != 0 else str(main_n)

    full_address = " ".join(
        filter(None, [sido, sigungu, eupmyeondong, donglee, f"{m}{detail}" if detail else None])
    )

    if dict_format:
        return AddressSchema(
            sido=sido,
            sigungu=sigungu,
            eupmyeondong=eupmyeondong,
            donglee=donglee,
            detail=f"{m}{detail}" if detail else None,
            fulladdr=full_address,
        )

    if scale > 0:
        return {1: sido, 2: sigungu, 3: eupmyeondong}.get(scale, full_address)

    return full_address
