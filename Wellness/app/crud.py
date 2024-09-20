from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app import models, recommend
from app.models import Recommend, Total_Today, History
from sqlalchemy.sql import func
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

def get_user_updated_at(db: Session, user_id: int):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            return user.updated_at
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to retrieve user update time.")
    raise HTTPException(status_code=404, detail="User not found.")

#사용자 ID를 기반으로 권장 영양소 정보 조회
def get_recommend_by_user_id(db: Session, user_id: int):
    try:
        recommendation = db.query(Recommend).filter(Recommend.user_id == user_id).first()
        if recommendation:
            return recommendation
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendation.")
    raise HTTPException(status_code=404, detail="Recommendation not found.")
 

#사용자의 권장 영양소 정보 생성 or 업데이트
def create_or_update_recommend(db: Session, user_id: int, rec_kcal: Decimal, rec_car: Decimal, rec_prot: Decimal, rec_fat: Decimal) -> models.Recommend:
    user_updated_at = get_user_updated_at(db, user_id)
    
    # Decimal 값을 소수점 두 자리까지 반올림
    rec_kcal = rec_kcal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_car = rec_car.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_prot = rec_prot.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_fat = rec_fat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    try:
        existing_recommend = get_recommend_by_user_id(db, user_id)
        if existing_recommend:
            if existing_recommend.updated_at < user_updated_at:
                existing_recommend.rec_kcal = rec_kcal
                existing_recommend.rec_car = rec_car
                existing_recommend.rec_prot = rec_prot
                existing_recommend.rec_fat = rec_fat
                existing_recommend.updated_at = func.now()
                db.commit()
                db.refresh(existing_recommend)
                return existing_recommend
        else:
            db_recommend = models.Recommend(
                user_id=user_id,
                rec_kcal=rec_kcal,
                rec_car=rec_car,
                rec_prot=rec_prot,
                rec_fat=rec_fat,
                updated_at=func.now()
            )
            db.add(db_recommend)
            db.commit()
            return db_recommend
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create or update recommendation.")

#특정 사용자와 날짜에 대한 Total_Today 레코드를 조회   
def get_total_today(db: Session, user_id: int, today: date):
    try:
        return db.query(models.Total_Today).filter(
                models.Total_Today.user_id == user_id,
                models.Total_Today.today == today
            ).first()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to retrieve total today record")
    return None
    
#총 섭취량을 조회하거나 새로 생성
def get_or_create_total_today(db: Session, user_id: int, date_obj: date):
    try:
        total_today = db.query(models.Total_Today).filter_by(user_id=user_id, today=date_obj).first()
        if total_today is None:
            total_today = models.Total_Today(
                user_id=user_id,
                total_kcal=Decimal('0'),
                total_car=Decimal('0'),
                total_prot=Decimal('0'),
                total_fat=Decimal('0'),
                condition=False,
                created_at=func.now(),
                updated_at=func.now(),
                today=date_obj,
                history_ids=[]
            )
            db.add(total_today)
            db.commit()
            db.refresh(total_today)
        return total_today
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to get or create total_today")


#사용자 권장 영양소를 조회하거나 업데이트
def get_or_update_recommendation(db: Session, user_id: int):
    try:
        recommendation = db.query(models.Recommend).filter(models.Recommend.user_id == user_id).first()
        if not recommendation:
            recommendation_result = recommend.recommend_nutrition(user_id, db)
            if recommendation_result["status"] == "success":
                return create_or_update_recommend(
                    db,
                    user_id,
                    Decimal(str(recommendation_result["rec_kcal"])),
                    Decimal(str(recommendation_result["rec_car"])),
                    Decimal(str(recommendation_result["rec_prot"])),
                    Decimal(str(recommendation_result["rec_fat"]))
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve recommendations")
        return recommendation
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

       
#Total_Today 레코드를 업데이트
from sqlalchemy.exc import SQLAlchemyError

def update_total_today(db: Session, total_today: models.Total_Today):
    try:
        total_today.updated_at = func.now()
        db.commit()
        db.refresh(total_today)
        return total_today
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update total today record")

