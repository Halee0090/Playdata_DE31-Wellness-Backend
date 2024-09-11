from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

class UserBase(BaseModel):
    age: int
    gender: int
    height: Decimal
    weight: Decimal
    birthday: date
    email: EmailStr
    nickname: str = Field(..., max_length=20)

class UserCreate(UserBase):
    age: int
    gender: int
    height: Decimal
    weight: Decimal
    birthday: date
    email: EmailStr
    nickname: str = Field(..., max_length=20)

class User(UserBase):
    id: int
    created_at: Optional[datetime]  # 자동 생성되므로 Optional로 지정
    updated_at: Optional[datetime]  # 자동 갱신되므로 Optional로 지정

    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    birthday: Optional[date] = None
    age: Optional[int] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None

# 응답 스키마 추가
class WellnessInfo(BaseModel):
    user_birthday: date
    user_age: int
    user_gender: int
    user_nickname: str
    user_height: Decimal
    user_weight: Decimal
    user_email: EmailStr

class UserResponseDetail(BaseModel):
    wellness_info: WellnessInfo

class UserResponse(BaseModel):
    status: str
    status_code: int
    detail: UserResponseDetail
    message: str

# 에러 응답 스키마
class ErrorResponse(BaseModel):
    status: str
    status_code: int
    message: str