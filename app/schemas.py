from pydantic import BaseModel


# 토큰 스키마
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str  # 새로 추가


class TokenRequest(BaseModel):
    username: str
    password: str