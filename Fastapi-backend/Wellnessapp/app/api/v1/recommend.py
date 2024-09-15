# /app/api/v1/recommend.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from api.v1.auth import validate_token
from db import crud, models
from db.session import get_db
from db.models import Auth, User
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging

router = APIRouter()

# 로깅 설정
logger = logging.getLogger(__name__)


@router.get("/eaten_nutrient")
async def get_recommend_eaten(
    today: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(validate_token)  # 토큰으로 인증된 사용자 정보
):
    logger.info(f"current_user: {current_user}, type: {type(current_user)}")
    
    # 문자열 date를 datetime 객체로 변환
    try:
        date_obj = datetime.strptime(today, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    
    # 사용자 정보 확인
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # current_user.id를 사용하여 권장 영양소 조회 및 업데이트
        recommendation = crud.get_or_update_recommendation(db, current_user.id)
    except HTTPException as e:
        logger.error(f"Error fetching recommendation: {str(e)}")
        raise e
    
    if recommendation is None:
        logger.error("Failed to retrieve or create recommendations")
        raise HTTPException(status_code=500, detail="Failed to retrieve or create recommendations")

    try:
        # current_user.id를 사용하여 총 섭취량 조회 또는 생성
        total_today = crud.get_or_create_total_today(db, current_user, date_obj)
    except HTTPException as e:
        logger.error(f"Error fetching or creating total_today: {str(e)}")
        raise e

    total_today.condition = total_today.total_kcal > recommendation.rec_kcal  
    crud.update_total_today(db, total_today)
    
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