from decimal import Decimal
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecommendBase(BaseModel):
    user_id: int
    rec_kcal: Decimal
    rec_car: Decimal
    rec_prot: Decimal
    rec_fat: Decimal

class RecommendCreate(RecommendBase):
    pass

class RecommendUpdate(RecommendBase):
    pass

class RecommendInDB(RecommendBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True
