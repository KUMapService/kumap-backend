from enum import Enum, IntEnum

class UserType(IntEnum):
    ADMIN = 0
    GENERAL = 1
    PREMIUM = 2

class ReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class Category(Enum):
    MT = "MT1"  # 대형마트
    CS = "CS2"  # 편의점
    PS = "PS3"  # 어린이집, 유치원
    SC = "SC4"  # 학교
    AC = "AC5"  # 학원
    PK = "PK6"  # 주차장
    OL = "OL7"  # 주유소, 충전소
    SW = "SW8"  # 지하철역
    BK = "BK9"  # 은행
    CT = "CT1"  # 문화시설
    AG = "AG2"  # 중개업소
    PO = "PO3"  # 공공기관
    AT = "AT4"  # 관광명소
    AD = "AD5"  # 숙박
    FD = "FD6"  # 음식점
    CE = "CE7"  # 카페
    HP = "HP8"  # 병원
    PM = "PM9"  # 약국

    @classmethod
    def list(cls, prefix=""):
        return [c.value + prefix for c in cls]

    @classmethod
    def place_code(cls) -> dict:
        return {
            cls.MT.value: "대형마트",
            cls.CS.value: "편의점",
            cls.PS.value: "어린이집 및 유치원",
            cls.SC.value: "학교",
            cls.AC.value: "학원",
            cls.PK.value: "주차장",
            cls.OL.value: "주유소 및 충전소",
            cls.SW.value: "지하철역",
            cls.BK.value: "은행",
            cls.CT.value: "문화시설",
            cls.AG.value: "중개업소",
            cls.PO.value: "공공기관",
            cls.AT.value: "관광명소",
            cls.AD.value: "숙박",
            cls.FD.value: "음식점",
            cls.CE.value: "카페",
            cls.HP.value: "병원",
            cls.PM.value: "약국",
        }
