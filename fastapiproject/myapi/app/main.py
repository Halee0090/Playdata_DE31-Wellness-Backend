from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from app import recommend, database, models, crud
from app.database import Base, engine
from sqlalchemy.orm import Session 
from sqlalchemy import func
from app.models import Total_Today, History
from datetime import date, datetime
from app.recommend import recommend_nutrition
from app.database import get_db
from decimal import Decimal, ROUND_HALF_UP
from typing import List
app = FastAPI(
    docs_url="/docs",  # Swagger UI 비활성화
    redoc_url="/redocs" 
)

Base.metadata.create_all(bind=engine)



@app.get("/recommend/eaten_nutrient")
def get_recommend_eaten(
    user_id: int, 
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    db: Session = Depends(get_db)
):
     # 문자열 date를 datetime 객체로 변환
    try:
         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    
    # 사용자 정보 확인
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # 사용자가 없을 경우
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
   
     # 권장 영양소 정보 확인 및 업데이트
    recommendation = crud.get_or_update_recommendation(db, user_id)
    if recommendation is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve or create recommendations")
    # 총 섭취량 조회 및 기본값 설정
    total_today = crud.get_or_create_total_today(db, user_id, date_obj)


    # condition 업데이트
    total_today.condition = total_today.total_kcal > recommendation.rec_kcal  
    crud.update_total_today(db,total_today)
    
    return {
    "status": "success",
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





@app.get("/history/meals")
def get_meal_history(
        user_id: int = Query(..., description="User id"),
        date: date = Query(..., description="Date of meals"),
        db: Session = Depends(get_db)
):
    try:

        total_today = crud.get_total_today(db, user_id, date)
        
        if total_today is None:
            raise HTTPException(status_code=404, detail="Total today recored not found")

        histories = crud.get_history_ids(db, total_today.history_ids)
        
        if histories is None:
            raise HTTPException(status_code=404, detail="No history records found")
        
        # total 정보 수집
        meals = []
        total_kcal = Decimal('0')
        total_car = Decimal('0')
        total_prot = Decimal('0')
        total_fat = Decimal('0')

        for history in histories:
            food = crud.get_food_id(db, history.food_id)
            meal_type = crud.get_meal_type_id(db, history.meal_type_id)

            if food is None or meal_type is None:
                continue  # meal_type 데이터 넣어야함!!!

            meals.append({
                    "meal_type": meal_type.type_name,
                    "food_name": food.food_name,
                    "food_kcal": food.food_kcal,
                    "food_car": food.food_car,
                    "food_prot": food.food_prot,
                    "food_fat": food.food_fat
                })
            
            # 총 영양소 계산
            total_kcal += food.food_kcal
            total_car += food.food_car
            total_prot += food.food_prot
            total_fat += food.food_fat

        # Total_Today 레코드 업데이트
        total_today.total_kcal = total_kcal
        total_today.total_car = total_car
        total_today.total_prot = total_prot
        total_today.total_fat = total_fat
        crud.update_total_today(db, total_today)

        return {
                "status": "success",
                "meals": meals,
                "total_kcal": Decimal(total_kcal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "total_car": Decimal(total_car).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "total_prot": Decimal(total_prot).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "total_fat": Decimal(total_fat).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))