from pydantic import BaseModel
from typing import Optional

class FoodListBase(BaseModel):
    category_id: int
    food_name: str
    category_name: str
    food_kcal: float
    food_car: float
    food_prot: float
    food_fat: float

class FoodListCreate(FoodListBase):
    pass

class FoodListUpdate(FoodListBase):
    pass

class FoodListInDB(FoodListBase):
    id: int

    class Config:
        orm_mode = True
