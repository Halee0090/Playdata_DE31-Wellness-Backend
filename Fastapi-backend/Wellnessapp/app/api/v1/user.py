from fastapi import APIRouter, HTTPException, Depends
from db import crud, models
import deps, schemas
from db.session import Session
from db.session import get_db
from schemas import UserCreate, UserResponse

router = APIRouter()
@router.post("/users_info", response_model=schemas.UserResponse)
def save_user_info(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 정보 저장
    try:
        new_user = crud.create_user(db=db, user=user)
        # 권장 영양소 계산 및 저장
        recommendation = crud.calculate_and_save_recommendation(db, new_user)
        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)
    except HTTPException as e:
        raise HTTPException(status_code=500, detail="Failed to create user") from e
    
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