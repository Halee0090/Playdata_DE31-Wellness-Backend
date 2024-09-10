from pydantic import BaseModel, EmailStr, constr
from datetime import date, datetime
from decimal import Decimal
from typing import ClassVar
from sqlalchemy import TIMESTAMP, Column
from sqlalchemy.sql import func

class UserBase(BaseModel):
    age: int
    gender: int
    height: Decimal
    weight: Decimal
    birthday: date
    email: EmailStr
    nickname: str = constr(max_length=20)

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: ClassVar[TIMESTAMP] = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: ClassVar[TIMESTAMP] = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    class Config:
        from_attributes = True  # 이전의 orm_mode = True

class UserUpdate(BaseModel):
    birthday: date
    age: int
    gender: int
    height: Decimal
    weight: Decimal
    email: EmailStr
    nickname: str = constr(max_length=20)

# 응답 스키마
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