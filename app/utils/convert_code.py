import csv
import os
from functools import lru_cache
from typing import Optional, Union, Dict

from app.core.config import settings

PNU_CODE_PATH = os.path.join(settings.BASE_DIR, "data", "PnuCode.csv")


@lru_cache(maxsize=1)
def load_pnu_mapping():
    with open(PNU_CODE_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))

@lru_cache(maxsize=1)
def load_pnu_lines():
    with open(PNU_CODE_PATH, encoding="utf-8") as f:
        return f.readlines()


def code2addr(code: str, scale: int = 0, dict_format: bool = False) -> Optional[Union[str, Dict[str, str]]]:
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
        return {
            "sido": sido,
            "sigungu": sigungu,
            "eupmyeondong": eupmyeondong,
            "donglee": donglee,
            "detail": f"{m}{detail}" if detail else None,
            "fulladdr": full_address,
        }

    if scale > 0:
        return {1: sido, 2: sigungu, 3: eupmyeondong}.get(scale, full_address)

    return full_address



def addr2code(addr: str):
    """주소를 PNU 코드로 변환"""
    pnu_reader = load_pnu_lines()
    pnuDict = {}
    for i in range(len(pnu_reader)):
        if i != 0:
            pnu_split = pnu_reader[i].split(",")
            for i in range(len(pnu_split)):
                if i == 0:
                    addr_str = ""
                    continue
                addr_str += pnu_split[i] + " "
            addr_str = addr_str.replace("\n ", "")
            addr_str = addr_str.rstrip(" ")
            pnuDict[addr_str] = pnu_split[0]
    addr = addr.rstrip().lstrip()
    addr_split = addr.split(" ")    # 공백을 기준으로 주소 분류
    addr_main = ""                  # 시/도, 시/군/구, 읍/면/동
    addr_sub_code = ""              # 지번
    for j in range(len(addr_split)):
        if j == len(addr_split) - 1:
            if addr_split[j][0] == "산":        # 필지가 산일 경우
                addr_split[j] = addr_split[j].lstrip("산")
                addr_sub_code += "2"
            elif addr_split[j][0] != "산":      # 필지가 일반일 경우
                addr_sub_code += "1"
            if len(addr_split[j].split("-")) == 2:  # 만일 부번이 있을 경우
                addr_sub_code += addr_split[j].split("-")[0].zfill(4)
                addr_sub_code += addr_split[j].split("-")[1].zfill(4)
            else:                                   # 부번이 없을 경우(본번만 있을 경우)
                addr_sub_code += addr_split[j].split("-")[0].zfill(4)
                addr_sub_code += "0000"
            break
        else:
            addr_main += str(addr_split[j]) + " "
    addr_main = addr_main.rstrip(" ")
    pnu = pnuDict[addr_main] + addr_sub_code
    return pnu
