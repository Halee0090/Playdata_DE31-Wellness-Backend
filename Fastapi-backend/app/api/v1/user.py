from fastapi import APIRouter, HTTPException, Depends
from app.db import models, crud
from app import deps, schemas
from app.db.session import Session
from app.db.session import get_db
from app.schemas import UserCreate, UserResponse
from app.services.recommend_service import recommend_nutrition


router = APIRouter()
@router.post("/users.info", response_model=schemas.UserResponse)
def save_user_info(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 사용자 정보 저장
    new_user = crud.create_user(db=db, user=user)
    try:
        # 권장 영양소 계산 및 저장
        recommend_nutrition(new_user.id, db)
    except HTTPException:
        # 권장 영양소 계산 중 오류 발생 시, 사용자 생성 후 에러 응답
        # 권장 영양소 계산이 실패한 경우 사용자 정보를 삭제할 수도 있지만,
        # 사용자 생성 후 에러 응답만 수행합니다.
        db.rollback()  # 사용자 생성은 완료되었으므로 롤백이 필요하지 않지만, 예외 처리로 인해 커밋을 롤백하는 것이 일반적입니다.
        raise HTTPException(status_code=500, detail="Failed to calculate nutrition recommendations")

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
        
