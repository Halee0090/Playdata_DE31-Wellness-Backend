# history.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.crud import create_history, get_meals_by_user_and_date
from db.models import History, Food_List, Meal_Type
from schemas.history import HistoryCreateRequest
from datetime import datetime


router = APIRouter()

@router.post("/save_and_get")
def save_to_history_and_get_today_history(
    history_data: HistoryCreateRequest,  
    db: Session = Depends(get_db)
):
    try:
        # 새 기록을 데이터베이스에 저장
        new_history = create_history(
            db=db,
            user_id=history_data.user_id,
            category_id=history_data.category_id,
            meal_type_id=history_data.meal_type_id,
            image_url=history_data.image_url,
            date=history_data.date
        )
        db.add(new_history)
        db.commit()

        # 기록과 음식 정보 조회
        meals = get_meals_by_user_and_date(db, history_data.user_id, history_data.date)

        # 응답 데이터 포맷팅
        meal_list = []
        for meal in meals:
            meal_list.append({
                "history_id": meal.history_id,
                "meal_type_name": meal.meal_type_name,
                "category_name": meal.category_name,
                "food_kcal": meal.food_kcal,
                "food_car": round(meal.food_car),
                "food_prot": round(meal.food_prot),
                "food_fat": round(meal.food_fat),
                "date": meal.date
            })
            
        return {
                "status": "success",
                "status_code": 201,  
                "detail": {
                            "Wellness_meal_list": meal_list  
                          },
                "message": "meal_list information saved successfully"
                }
        
    except Exception as e:
        print(f"Error: {e}")  # 오류를 콘솔에 출력
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")
