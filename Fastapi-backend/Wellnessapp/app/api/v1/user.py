from fastapi import APIRouter, HTTPException, Depends
from Wellnessapp.app.db import models, crud
from Wellnessapp.app import deps, schemas
from Wellnessapp.app.db.session import Session
from Wellnessapp.app.db.session import get_db
from Wellnessapp.app.schemas import UserCreate, UserResponse


router = APIRouter()
@router.post("/users_info", response_model=schemas.UserResponse)
def save_user_info(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 정보 저장
    new_user = crud.create_user(db=db, user=user)

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
            }
        },
        "message": "User information saved successfully"
    }
        