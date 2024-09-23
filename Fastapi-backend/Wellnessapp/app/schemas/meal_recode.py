from pydantic import BaseModel
from typing import List
from date import datetime

class MealRecord(BaseModel):
    history_id: int
    meal_type_name: str
    category_name: str
    food_kcal: float
    food_car: float
    food_prot: float
    food_fat: float
    date: datetime

class WellnessMealListResponse(BaseModel):
    Wellness_meal_list: List[MealRecord]

class ResponseModel(BaseModel):
    status: str
    status_code: int
    detail: WellnessMealListResponse
    message: str