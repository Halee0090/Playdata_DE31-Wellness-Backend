from sqlalchemy.orm import Session
from app.models import FoodList, Recommend, Userinfo
from fastapi import HTTPException


def get_food_by_category(db: Session, category_id: int) -> FoodList:
     food_item = db.query(FoodList).filter(FoodList.category_id == category_id).first()
     
     if not food_item:
          raise HTTPException(status_code=404, detail="Food category not found")
     
     return food_item

def get_recommend_by_user(db: Session, user_id: int) -> Recommend:
     Recommendation = db.query(Recommend).filter(Recommend.user_id == user_id).first()
     
     if not Recommendation:
          raise HTTPException(status_code=400, detail="Recommendation not found")
     
     return Recommendation


