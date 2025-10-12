from pydantic import BaseModel


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: str

class DuplicateCheckDTO(BaseModel):
    email_available: bool
    nickname_available: bool
