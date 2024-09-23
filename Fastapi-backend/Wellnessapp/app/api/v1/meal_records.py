from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.session import get_db
from db.crud import get_meals_by_user_and_date
from api.v1.auth import validate_token
from db.models import User
from datetime import datetime, date
import logging
from decimal import Decimal

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def datetime_to_string(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

@router.get("/meal_records")
async def get_meal_records(
    date: date = Query(..., description="Date to retrieve meals for (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(validate_token)
):
    try:
        # 날짜 형식 확인
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # 사용자의 식사 기록 조회
        meals = get_meals_by_user_and_date(db, current_user, date)
        logger.info(f"Retrieved {len(meals)} meals for user {current_user.id} on {date}")

        # 응답 데이터 포맷팅
        meal_list = []
        for meal in meals:
            meal_list.append({
                "history_id": meal.history_id,
                "meal_type_name": meal.meal_type_name.encode('utf-8').decode('utf-8'),
                "category_name": meal.category_name.encode('utf-8').decode('utf-8'),
                "food_kcal": decimal_to_float(meal.food_kcal),
                "food_car": round(decimal_to_float(meal.food_car)),
                "food_prot": round(decimal_to_float(meal.food_prot)),
                "food_fat": round(decimal_to_float(meal.food_fat)),
                "date": datetime_to_string(meal.date)
            })

        return JSONResponse(
            content={
                "status": "success",
                "status_code": 200,
                "detail": {
                    "Wellness_meal_list": meal_list
                },
                "message": "Meal records retrieved successfully"
            },
            media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        logger.error(f"Failed to retrieve meal records: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving meal records")