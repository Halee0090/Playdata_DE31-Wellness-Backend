from pydantic import BaseModel

# 클라이언트에게 반환될 토큰 스키마
class Token(BaseModel):
    access_token: str
    token_type: str

# 토큰에서 추출된 데이터 (user_id 필수)
class TokenData(BaseModel):
    user_id: int  # 필수 필드로 설정
