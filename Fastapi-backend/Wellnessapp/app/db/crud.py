# crud.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from services import recommend_service
from api.v1 import recommend
from db.models import Food_List, Recommend, Total_Today, History, Meal_Type
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from db.models import Food_List, Recommend, Total_Today
from datetime import date, datetime
from api.v1 import recommend
from db import models
from schemas import UserCreate
import schemas
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


# 공통 예외 처리 헬퍼 함수
def execute_db_operation(db: Session, operation):
    try:
        result = operation()
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed: {str(e)}")


# 사용자의 마지막 업데이트 시간 조회
# def get_user_updated_at(db: Session, user_id: int):
#     return execute_db_operation(db, lambda: db.query(models.User).filter(models.User.id == user_id).first())
def get_user_updated_at(db: Session, user_id: int):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.updated_at
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 사용자 ID로 권장 영양소 조회
# def get_recommend_by_user_id(db: Session, user_id: int):
#     return execute_db_operation(db, lambda: db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first())
def get_recommend_by_user_id(db: Session, user_id: int):
    try:
        recommend = db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first()
        return recommend
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
              

# 권장 영양소 생성 및 업데이트
# def create_or_update_recommend(db: Session, user_id: int, rec_kcal: Decimal, rec_car: Decimal, rec_prot: Decimal, rec_fat: Decimal):
#     user_updated_at = get_user_updated_at(db, user_id)
    
#     # Decimal 값을 소수점 두 자리까지 반올림
#     rec_kcal = rec_kcal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     rec_car = rec_car.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     rec_prot = rec_prot.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     rec_fat = rec_fat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#     def operation():
#         existing_recommend = get_recommend_by_user_id(db, user_id)
#         if existing_recommend and existing_recommend.updated_at < user_updated_at:
#             existing_recommend.rec_kcal, existing_recommend.rec_car, existing_recommend.rec_prot, existing_recommend.rec_fat = rec_kcal, rec_car, rec_prot, rec_fat
#             existing_recommend.updated_at = func.now()
#             db.refresh(existing_recommend)
#             return existing_recommend
#         else:
#             new_recommend = models.Recommend(
#                 user_id=user_id, rec_kcal=rec_kcal, rec_car=rec_car, rec_prot=rec_prot, rec_fat=rec_fat, updated_at=func.now()
#             )
    #         db.add(new_recommend)
    #         return new_recommend
    
    # return execute_db_operation(db, operation)

       
    
        
def calculate_and_save_recommendation(db: Session, user: models.User):
    recommendation_result = recommend_service.recommend_nutrition(user.weight, user.height, user.age, user.gender)
    return models.Recommend(
        user_id=user.id,
        rec_kcal=recommendation_result["rec_kcal"],
        rec_car=recommendation_result["rec_car"],
        rec_prot=recommendation_result["rec_prot"],
        rec_fat=recommendation_result["rec_fat"]
    )
# 총 섭취량 조회 또는 생성
<<<<<<< HEAD
def get_or_create_total_today(db: Session, current_user: models.User, date_obj: date):
    try:
        total_today = db.query(models.Total_Today).filter_by(user_id=current_user.id, today=date_obj).first()
=======
# def get_or_create_total_today(db: Session, user_id: int, date_obj: date):
#     def operation():
#         total_today = db.query(models.Total_Today).filter_by(user_id=user_id, today=date_obj).first()
#         if total_today is None:
#             total_today = models.Total_Today(
#                 user_id=user_id, total_kcal=Decimal('0'), total_car=Decimal('0'),
#                 total_prot=Decimal('0'), total_fat=Decimal('0'), condition=False,
#                 created_at=func.now(), updated_at=func.now(), today=date_obj, history_ids=[]
#             )
#             db.add(total_today)
#             db.refresh(total_today)
#         return total_today
#     return execute_db_operation(db, operation)
def get_or_create_total_today(db: Session, user_id: int, date_obj: date):
    try:
        total_today = db.query(models.Total_Today).filter_by(user_id=user_id, today=date_obj).first()
        if total_today is None:
            total_today = models.Total_Today(
                user_id=current_user.id, total_kcal=Decimal('0'), total_car=Decimal('0'),
                total_prot=Decimal('0'), total_fat=Decimal('0'), condition=False,
                created_at=func.now(), updated_at=func.now(), today=date_obj, history_ids=[]
            )
            db.add(total_today)
            db.commit()
            db.refresh(total_today)
        return total_today
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data: Integrity constraint violated")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Total_Today 업데이트
# def update_total_today(db: Session, total_today: models.Total_Today):
#     return execute_db_operation(db, lambda: db.refresh(total_today))
def update_total_today(db: Session, total_today: models.Total_Today):
    try:
        db.refresh(total_today)
        db.commit()
        return total_today
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update Total_Today: {str(e)}")

# 사용자 권장 영양소를 조회하거나 업데이트
# def get_or_update_recommendation(db: Session, user_id: int):
#     recommendation = get_recommend_by_user_id(db, user_id)
#     if not recommendation:
#         recommendation_result = recommend.recommend_nutrition(user_id, db)
#         if recommendation_result["status"] == "success":
#             return create_or_update_recommend(
#                 db,
#                 user_id,
#                 Decimal(recommendation_result["rec_kcal"]),
#                 Decimal(recommendation_result["rec_car"]),
#                 Decimal(recommendation_result["rec_prot"]),
#                 Decimal(recommendation_result["rec_fat"]),
#             )
#         else:
#             raise HTTPException(status_code=500, detail="Failed to retrieve recommendations")
#     return recommendation
def get_or_update_recommendation(db: Session, user_id: int):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        recommendation = db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first()
        # 추천 정보가 없거나 사용자 정보가 최근에 업데이트된 경우
        if not recommendation or recommendation.updated_at < user.updated_at:
            # 새로운 추천 영양소 계산
            new_values = recommend_service.recommend_nutrition(user.weight, user.height, user.age, user.gender)
            
            if not recommendation:
                recommendation = models.Recommend(user_id=user_id)
                db.add(recommendation)
            
            recommendation.rec_kcal = new_values["rec_kcal"]
            recommendation.rec_car = new_values["rec_car"]
            recommendation.rec_prot = new_values["rec_prot"]
            recommendation.rec_fat = new_values["rec_fat"]
            recommendation.updated_at = func.now()
            
            db.commit()
            db.refresh(recommendation)
        total_today = get_or_create_total_today(db, user_id, date.today())
        new_condition = total_today.total_kcal > recommendation.rec_kcal
        update_total_today_condition(db, total_today.id, new_condition)

        return recommendation

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data: Integrity constraint violated")
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data: Data type mismatch")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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
 
def create_history(db: Session, user_id: int, category_id: int, meal_type_id: int, image_url: str, date: date):
    new_history = History(
        user_id=user_id,
        category_id=category_id,
        meal_type_id=meal_type_id,
        image_url=image_url,
        date=date
    )
    db.add(new_history)
    return new_history

def get_today_history(db: Session, user_id: int, today: date):
    return db.query(History).filter(
        History.user_id == user_id,
        History.date == Total_Today.today
    ).all()

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

def get_meals_by_user_and_date(db: Session, user_id: int, date: datetime):
    meals = db.query(
        History.id.label("history_id"),
        Meal_Type.type_name.label("meal_type_name"),
        Food_List.category_name,
        Food_List.food_kcal,
        Food_List.food_car,
        Food_List.food_prot,
        Food_List.food_fat,
        History.date
    ).join(Food_List, History.category_id == Food_List.category_id) \
     .join(Meal_Type, History.meal_type_id == Meal_Type.id) \
     .filter(History.date == date) \
     .filter(History.user_id == user_id) \
     .all()
    return meals

def update_total_today_condition(db: Session, total_today_id: int, new_condition: bool):
    total_today = db.query(models.Total_Today).filter(models.Total_Today.id == total_today_id).first()
    if total_today:
        total_today.condition = new_condition
        db.commit()
        db.refresh(total_today)
        return total_today
    return None

def update_total_today_condition(db: Session, total_today_id: int, new_condition: bool):
    try:
        total_today = db.query(models.Total_Today).filter(models.Total_Today.id == total_today_id).first()
        if total_today:
            if total_today.condition != new_condition:
                total_today.condition = new_condition
                db.commit() 
                db.refresh(total_today)  
        
        return total_today

    except SQLAlchemyError as e:
        db.rollback()  
        print(f"Database error occurred: {e}")
        return None

    except Exception as e:
        db.rollback()  
        print(f"An unexpected error occurred: {e}")
        return None
