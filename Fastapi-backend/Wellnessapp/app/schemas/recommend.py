from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecommendBase(BaseModel):
    user_id: int
    rec_kcal: float
    rec_car: float
    rec_prot: float
    rec_fat: float

class RecommendCreate(RecommendBase):
    pass

class RecommendUpdate(RecommendBase):
    pass

class RecommendInDB(RecommendBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True
