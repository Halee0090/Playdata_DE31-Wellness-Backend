from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Food_List, Recommend
from app.db import models
from sqlalchemy.sql import func
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from app.api.v1 import recommend
from app.db import models
from app.schemas import UserCreate
from app import schemas
from app.services.recommend_service import recommend_nutrition
# 공통 예외 처리 헬퍼 함수
def execute_db_operation(db: Session, operation):
    try:
        result = operation()
        db.commit()
        return result
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")

# 사용자의 마지막 업데이트 시간 조회
def get_user_updated_at(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user.updated_at
    else:
        raise HTTPException(status_code=404, detail="User not found")
# 사용자 ID로 권장 영양소 조회
def get_recommend_by_user_id(db: Session, user_id: int):
    return execute_db_operation(db, lambda: db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first())


def create_or_update_recommend(db: Session, user_id: int, rec_kcal: Decimal, rec_car: Decimal, rec_prot: Decimal, rec_fat: Decimal):
    user_updated_at = get_user_updated_at(db, user_id)
    
    # Decimal 값을 소수점 두 자리까지 반올림
    rec_kcal = rec_kcal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_car = rec_car.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_prot = rec_prot.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_fat = rec_fat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def operation():
        existing_recommend = get_recommend_by_user_id(db, user_id)
        if existing_recommend:
            if existing_recommend.updated_at < user_updated_at:
                existing_recommend.rec_kcal = rec_kcal
                existing_recommend.rec_car = rec_car
                existing_recommend.rec_prot = rec_prot
                existing_recommend.rec_fat = rec_fat
                existing_recommend.updated_at = func.now()
            return existing_recommend
        else:
            new_recommend = models.Recommend(
                user_id=user_id,
                rec_kcal=rec_kcal,
                rec_car=rec_car,
                rec_prot=rec_prot,
                rec_fat=rec_fat,
                updated_at=func.now()
            )
            db.add(new_recommend)
            return new_recommend
    
    return execute_db_operation(db, operation)
# 총 섭취량 조회 또는 생성
def get_or_create_total_today(db: Session, user_id: int, date_obj: date):
    def operation():
        total_today = db.query(models.Total_Today).filter_by(user_id=user_id, today=date_obj).first()
        if total_today is None:
            total_today = models.Total_Today(
                user_id=user_id, total_kcal=Decimal('0'), total_car=Decimal('0'),
                total_prot=Decimal('0'), total_fat=Decimal('0'), condition=False,
                created_at=func.now(), updated_at=func.now(), today=date_obj, history_ids=[]
            )
            db.add(total_today)
            db.refresh(total_today)
        return total_today
    return execute_db_operation(db, operation)

# Total_Today 업데이트
def update_total_today(db: Session, total_today: models.Total_Today):
    return execute_db_operation(db, lambda: db.refresh(total_today))

# 사용자 권장 영양소를 조회하거나 업데이트
def get_or_update_recommendation(db: Session, user_id: int):
    recommendation = get_recommend_by_user_id(db, user_id)
    if not recommendation:
        try:
            recommendation_result = recommend_nutrition(user_id, db)
            if recommendation_result["status"] == "success":
                return create_or_update_recommend(
                    db,
                    user_id,
                    Decimal(recommendation_result["rec_kcal"]),
                    Decimal(recommendation_result["rec_car"]),
                    Decimal(recommendation_result["rec_prot"]),
                    Decimal(recommendation_result["rec_fat"]),
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve recommendations")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process recommendation: {str(e)}")
    return recommendation

def get_food_by_category(db: Session, category_id: int) -> Food_List:
     food_item = db.query(Food_List).filter(Food_List.category_id == category_id).first()
     
     if not food_item:
          raise HTTPException(status_code=404, detail="Food category not found")
     
     return food_item


def get_recommend_by_user(db: Session, user_id: int) -> Recommend:
     Recommendation = db.query(Recommend).filter(Recommend.user_id == user_id).first()
     
     if not Recommendation:
          raise HTTPException(status_code=400, detail="Recommendation not found")
     
     return Recommendation

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        birthday=user.birthday,
        age=user.age,
        gender=user.gender,
        nickname=user.nickname,
        height=user.height,
        weight=user.weight,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user