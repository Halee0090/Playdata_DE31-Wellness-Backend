    # /app/api/v1/recommend.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from api.v1 import model
from services.auth_service import validate_token
from db import crud, models
from db.session import get_db
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from db.models import User, Recommend
import logging
logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/eaten_nutrient")
def get_recommend_eaten(
    today: str = Query(None, description="The date for recommendation in YYYY-MM-DD format"),  # today를 쿼리 매개변수로 처리
    db: Session = Depends(get_db),
    current_user: models.User = Depends(validate_token)     
):
    
    # 만약 today 값이 전달되지 않았다면, 현재 서버 날짜로 설정
    if not today:
        today = datetime.now().strftime("%Y-%m-%d")
    
    # 로그 추가: current_user 확인
    logger.info(f"current_user: {current_user}, type: {type(current_user)}")
    
    # 문자열 date를 datetime 객체로 변환
    try:
        date_obj = datetime.strptime(today, "%Y-%m-%d").date()
    except ValueError:
        logger.error("Invalid date format. Please use YYYY-MM-DD.")# 에러 응답 형식 변경(09.17 17:41)
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    
# 사용자 정보 확인
    if current_user is None:
        logger.error("User not found")# 에러 응답 형식 변경(09.17 17:41)
        raise HTTPException(status_code=404, detail="User not found")
    try:
        # 권장 영양소 조회
        recommendation = crud.get_or_update_recommendation(db, current_user)
    except HTTPException as e:
        logger.error(f"Error retrieving recommendations: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    if recommendation is None:
        logger.error("Failed to retrieve or create recommendations")
        raise HTTPException(status_code=404, detail="Failed to retrieve or create recommendations")
    # 오늘의 총 섭취량 조회 또는 생성
    try:
        total_today = crud.get_total_today(db, current_user, date_obj)
    except HTTPException as e:
        logger.error(f"Error retrieving or creating total_today: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        # raise HTTPException(status_code=500, detail="Unexpected server error")
        raise HTTPException(status_code=500, detail="Unexpected server error")
        
    if total_today is not None:
        total_today.condition = total_today.total_kcal > recommendation.rec_kcal
    else:
        raise HTTPException(status_code=404, detail="total_today not found")
    
    # total_today 업데이트
    try:
        crud.update_total_today(db, total_today)
    except Exception as e:
        logger.error(f"Failed to update total_today: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update total_today")
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
        "message": "Wellness user's total intake and recommended values have been successfully retrieved."
    }