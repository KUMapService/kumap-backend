from pydantic import BaseModel, Field


# REQUEST DATA
class LandOwnerRequest(BaseModel):
    pnu: str = Field(..., description="PNU코드")
    lat: float = Field(None, description="위도")
    lng: float = Field(None, description="경도")
