from decimal import Decimal
from pydantic import BaseModel
<<<<<<< HEAD
=======
from typing import Optional
from decimal import Decimal

>>>>>>> 09710e7dc49ffc696602f6f8ac7d6ccb4efb4259

class FoodListBase(BaseModel):
    category_id: int
    food_name: str
    category_name: str
    food_kcal: Decimal
    food_car: Decimal
    food_prot: Decimal
    food_fat: Decimal

class FoodListCreate(FoodListBase):
    pass

class FoodListUpdate(FoodListBase):
    pass

class FoodListInDB(FoodListBase):
    id: int

    class Config:
        orm_mode = True