from pydantic import BaseModel, EmailStr, Field
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
    nickname: str = Field(max_length=20)

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
<<<<<<< HEAD

=======
>>>>>>> 09710e7dc49ffc696602f6f8ac7d6ccb4efb4259
    class Config:
        from_attributes = True  

class UserUpdate(BaseModel):
    birthday: date
    age: int
    gender: int
    height: Decimal
    weight: Decimal
    email: EmailStr
    nickname: str = Field(max_length=20)

class WellnessInfo(BaseModel):
    user_birthday: date
    user_age: int
    user_gender: int
    user_nickname: str
    user_height: Decimal
    user_weight: Decimal
    user_email: EmailStr
    user_nickname: str = Field(max_length=20)

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