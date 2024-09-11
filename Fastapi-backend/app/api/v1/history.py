from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.crud import create_history, get_today_history
from datetime import datetime, date

router = APIRouter()

@router.post("/save_and_get")
def save_to_history_and_get_today_history(
    user_id: int, 
    category_id: int, 
    meal_type_id: int, 
    image_url: str, 
    date: datetime, 
    db: Session = Depends(get_db)
):
    try:
        new_history = create_history(
            db=db,
            user_id=user_id,
            category_id=category_id,
            meal_type_id=meal_type_id,
            image_url=image_url,
            date=date
        )
        db.commit()
        
        # 2. 오늘의 기록 조회
        today = date.today()
        today_history = get_today_history(db, user_id, today)

        # 3. 조회된 오늘의 기록을 리스트 형식으로 반환
        history_list = [
            {
                "history_id": hist.id,  # history의 고유 ID
                "meal_type": hist.meal.type_name,  # 아침, 점심, 저녁 등의 식사 유형
                "food_name": hist.food.food_name,  # 음식 이름
                "food_kcal": hist.food.food_kcal,  # 음식의 칼로리
                "food_car": hist.food.food_car,  # 탄수화물
                "food_prot": hist.food.food_prot,  # 단백질
                "food_fat": hist.food.food_fat,  # 지방
            }
            for hist in today_history
        ]

        return {
            "status": "success",
            "message": "History saved successfully",
            "detail": history_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")
