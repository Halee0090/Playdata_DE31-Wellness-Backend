from pydantic import BaseModel
from decimal import Decimal
from typing import ClassVar
from sqlalchemy import TIMESTAMP, Column
from sqlalchemy.sql import func


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
    updated_at: ClassVar[TIMESTAMP] = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True
