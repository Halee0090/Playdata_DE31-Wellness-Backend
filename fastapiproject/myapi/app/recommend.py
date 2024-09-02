# 

from sqlalchemy.orm import Session
from app import crud, models
from fastapi import HTTPException
from datetime import datetime

def recommend_nutrition(user_id: int, db: Session):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=400, 
                detail={"status": "error", "message": "Invalid user_id"}
            )
        
        # 기존 권장 영양소 정보 조회
        existing_recommendation = db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first()
        
        # 사용자 정보가 업데이트되었거나 권장 영양소 정보가 없는 경우에만 새로 계산
        if not existing_recommendation or existing_recommendation.updated_at < user.updated_at:
            # BMR 계산 (해리스-베네딕트 방정식 사용)
            if user.gender == 1:  # 남성이 1이라 가정
                bmr = 88.362 + (13.397 * user.weight) + (4.799 * user.height) - (5.677 * user.age)
            else:  # 남성이 아닌 경우 여성이라 가정
                bmr = 447.593 + (9.247 * user.weight) + (3.098 * user.height) - (4.330 * user.age)

            rec_kcal = bmr * 1.55  # 보통 활동량이라고 가정

            # 탄, 단, 지 비율 설정 5:3:2
            rec_car = (rec_kcal * 0.5) / 4  # 1g 4kcal
            rec_prot = (rec_kcal * 0.3) / 4  # 1g 4kcal
            rec_fat = (rec_kcal * 0.2) / 9  # 1g 9kcal

            # 데이터베이스에 저장 또는 업데이트
            recommendation = crud.create_or_update_recommend(db, user_id, rec_kcal, rec_car, rec_prot, rec_fat)
        else:
            # 기존 권장 영양소 정보 사용
            recommendation = existing_recommendation

        return {
            "status": "success",
            "rec_kcal": round(recommendation.rec_kcal, 2),
            "rec_car": round(recommendation.rec_car, 2),
            "rec_prot": round(recommendation.rec_prot, 2),
            "rec_fat": round(recommendation.rec_fat, 2),
            "last_updated": recommendation.updated_at
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": "Internal server error. Please try again later."}
        )