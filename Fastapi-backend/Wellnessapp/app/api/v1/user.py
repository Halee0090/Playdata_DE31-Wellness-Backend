from fastapi import APIRouter, HTTPException, Depends
from db import crud, models
import deps, schemas
from db.session import Session
from db.session import get_db
from schemas import UserCreate, UserResponse
from datetime import date
import logging

logger = logging.getLogger(__name__)


router = APIRouter()

@router.post("/users_info", response_model=schemas.UserResponse)
def save_user_info(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    

    try:
        # 사용자 정보 저장
        new_user = crud.create_user(db=db, user=user)
        
        # 권장 영양소 계산 및 저장
        recommendation = crud.calculate_and_save_recommendation(db, new_user)
        db.add(recommendation)
        db.flush()  # 이 시점에서 recommendation에 id가 할당
        
        # total_today 생성
        today = date.today()
        total_today = crud.get_or_create_total_today(db, new_user.id, today)
    
        db.commit()
        db.refresh(recommendation)
        db.refresh(new_user)
        db.refresh(total_today)
    except HTTPException as e:
        db.rollback()
        logger.info(f"Creating total_today for user: {new_user.id} on date: {today}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}") from e    
    
    # response에 user_info, recommen, total_today 값 확인할 수 있도록 추가함

    return {
        "status": "success",
        "status_code": 201,
        "detail": {
            "wellness_info": {
                "user_email": new_user.email,
                "user_nickname": new_user.nickname,
                "user_birthday": new_user.birthday,
                "user_gender": new_user.gender,
                "user_height": new_user.height,
                "user_weight": new_user.weight,
                "user_age": new_user.age,
            },
            "recommendations": {
                "rec_kcal": recommendation.rec_kcal,
                "rec_car": recommendation.rec_car,
                "rec_prot": recommendation.rec_prot,
                "rec_fat": recommendation.rec_fat
            },
            "total_today": {
                "total_kcal": total_today.total_kcal,
                "total_car": total_today.total_car,
                "total_prot": total_today.total_prot,
                "total_fat": total_today.total_fat,
                "condition": total_today.condition
            }
        },
        "message": "User information and recommendations, and total_today saved successfully"
    }