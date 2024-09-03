from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from app import recommend, database, models, crud
from app.database import Base, engine
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Total_Today
from datetime import date, datetime
from app.recommend import recommend_nutrition
from app.database import get_db


app = FastAPI(
    docs_url="/docs",  # Swagger UI 비활성화
    redoc_url="/redocs" 
)

Base.metadata.create_all(bind=engine)



@app.get("/recommend/eaten_nutrient")
def get_recommend_eaten(
    user_id: int, 
    date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$"),
    db: Session = Depends(get_db)
):
     # 문자열 date를 datetime 객체로 변환
    try:
         date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    # 사용자 정보 확인
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 권장 영양소 정보 확인 및 업데이트
    recommendation = get_or_update_recommendation(user_id, db)
    
    # 총 섭취량 조회 및 기본값 설정
    total_today = get_or_create_total_today(user_id, date, db)
    
    return {
        "status": "success",
        "total_kcal": round(total_today.total_kcal, 2),
        "total_car": round(total_today.total_car,  2),
        "total_prot": round(total_today.total_prot, 2),
        "total_fat": round(total_today.total_fat, 2),
        "rec_kcal": round(recommendation.rec_kcal, 2),
        "rec_car": round(recommendation.rec_car, 2),
        "rec_prot": round(recommendation.rec_prot, 2),
        "rec_fat": round(recommendation.rec_fat, 2),
        "condition": total_today.condition
    }

def get_or_update_recommendation(user_id: int, db: Session):
    """사용자 권장 영양소를 조회하거나 업데이트합니다."""
    recommendation = db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first()
    if not recommendation:
        # 권장 영양소가 없는 경우 새로 계산 및 저장
        recommendation_result = recommend.recommend_nutrition(user_id, db)
        if recommendation_result["status"] == "success":
            recommendation = crud.create_or_update_recommend(
                db,
                user_id,
                recommendation_result["rec_kcal"],
                recommendation_result["rec_car"],
                recommendation_result["rec_prot"],
                recommendation_result["rec_fat"]
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update recommendations")
    return recommendation

def get_or_create_total_today(user_id: int, date: date, db: Session):
    """총 섭취량을 조회하거나 새로 생성합니다."""
    total_today = db.query(models.Total_Today).filter_by(user_id=user_id, date=date).first()
    if not total_today:
        total_today = models.Total_Today(
            user_id=user_id,
            total_kcal=0,
            total_car=0,
            total_prot=0,
            total_fat=0,
            condition=False,
            created_at=func.now(),
            updated_at=func.now(),
            date=date,
            history_ids=[]
        )
        db.add(total_today)
        db.commit()
        db.refresh(total_today)
    return total_today