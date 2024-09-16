from fastapi import APIRouter, HTTPException, Depends, status
from db import crud, models
import schemas
from db.session import get_db
from sqlalchemy.orm import Session
from api.v1.auth import validate_token  # 토큰 검증 함수 가져오기
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 사용자 정보 저장 API (토큰 필수)
@router.post("/users_info", response_model=schemas.UserResponse)
def save_user_info(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(validate_token)  # 토큰 검증된 사용자 정보
):
    if not current_user:
        # 토큰이 없는 경우 명확히 예외를 발생시킵니다.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided"
        )
    
    # 이메일 중복 체크
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 정보 저장 (토큰 검증 통과 후 실행)
    try:
        new_user = crud.create_user(db=db, user=user)
        # 권장 영양소 계산 및 저장
        recommendation = crud.calculate_and_save_recommendation(db, new_user)
        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)
    except Exception as e:
        logger.error(f"Error saving user info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return {
        "status": "success",
        "status_code": 201,
        "detail": {
            "wellness_info": {
                "user_birthday": new_user.birthday,
                "user_age": new_user.age,
                "user_gender": new_user.gender,
                "user_nickname": new_user.nickname,
                "user_height": new_user.height,
                "user_weight": new_user.weight,
                "user_email": new_user.email
            },
            "recommendations": {
                "rec_kcal": recommendation.rec_kcal,
                "rec_car": recommendation.rec_car,
                "rec_prot": recommendation.rec_prot,
                "rec_fat": recommendation.rec_fat
            }
        },
        "message": "User information and recommendations saved successfully"
    }
