from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models
from app.models import Recommend
from sqlalchemy.sql import func
from decimal import Decimal, ROUND_HALF_UP

def get_user_updated_at(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user.updated_at
    return None

def get_recommend_by_user_id(db: Session, user_id:int):
    return db.query(Recommend).filter(Recommend.user_id == user_id).first()


def create_or_update_recommend(db: Session, user_id: int, rec_kcal: Decimal, rec_car: Decimal, rec_prot: Decimal, rec_fat: Decimal) -> models.Recommend:
    user_updated_at = get_user_updated_at(db, user_id)
    
    if user_updated_at is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_recommend = get_recommend_by_user_id(db, user_id)
    
    # Decimal 값을 소수점 두 자리까지 반올림
    rec_kcal = rec_kcal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_car = rec_car.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_prot = rec_prot.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rec_fat = rec_fat.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    if existing_recommend: #객체가 실제로 존재한다면
        if existing_recommend.updated_at < user_updated_at:
            # Update existing recommendation
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
        db.refresh(db_recommend)
        return db_recommend
    
