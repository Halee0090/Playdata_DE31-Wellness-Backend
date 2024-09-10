from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HistoryBase(BaseModel):
    user_id: int
    food_id: int
    meal_type_id: int
    image_url: str
    date: datetime

class HistoryCreate(HistoryBase):
    pass

class HistoryUpdate(HistoryBase):
    pass

class HistoryInDB(HistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
