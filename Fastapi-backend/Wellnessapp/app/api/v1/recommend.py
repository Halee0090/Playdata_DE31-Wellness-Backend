# /app/api/v1/recommend.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from db import crud, models
from db.session import get_db
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from db.models import User, Recommend

router = APIRouter()

@router.get("/eaten_nutrient")
def get_recommend_eaten(
    user_id: int, 
    today: str = Query(...),
    db: Session = Depends(get_db)
):
    # 문자열 date를 datetime 객체로 변환
    try:
        date_obj = datetime.strptime(today, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    
    # 사용자 정보 확인
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        recommendation = crud.get_or_update_recommendation(db, user_id)
    except HTTPException as e:
        raise e
    
    if recommendation is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve or create recommendations")

    try:
        total_today = crud.get_or_create_total_today(db, user_id, date_obj)
    except HTTPException as e:
        raise e

    total_today.condition = total_today.total_kcal > recommendation.rec_kcal  
    crud.update_total_today(db,total_today)
    
    return {
        "status": "success",
        "status_code": 200,
        "detail": {
            "wellness_recommend_info": {
                "total_kcal": Decimal(total_today.total_kcal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "total_car": Decimal(total_today.total_car).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "total_prot": Decimal(total_today.total_prot).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "total_fat": Decimal(total_today.total_fat).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "rec_kcal": Decimal(recommendation.rec_kcal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "rec_car": Decimal(recommendation.rec_car).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "rec_prot": Decimal(recommendation.rec_prot).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "rec_fat": Decimal(recommendation.rec_fat).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                 "condition": total_today.condition
                    }
                },
        "message": "User recommend information saved successfully"
            }

