from sqlalchemy import ForeignKey, Column, Integer, String, Float, DateTime, TIMESTAMP, Boolean, ARRAY
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user_info'

    id = Column(Integer, primary_key=True,  autoincrement=True)
    nickname = Column(String(30), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    birthday = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    
class Recommend(Base):
    __tablename__ = 'recommend'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    rec_kcal = Column(Float, nullable=False)
    rec_car = Column(Float, nullable=False)
    rec_prot = Column(Float, nullable=False)
    rec_fat = Column(Float, nullable=False)
    created_at = Column(DateTime,  default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class Food_List(Base):
    __tablename__ = 'food_list'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, nullable=False)
    food_name = Column(String(15), nullable=False)
    category_name = Column(String(10), nullable=False)
    food_kcal = Column(Float, nullable=False)
    food_car = Column(Float, nullable=False)
    food_prot = Column(Float, nullable=False)
    food_fat = Column(Float, nullable=False)


class Meal_Type(Base):
    __tablename__ = 'meal_type'
    id = Column(Integer, primary_key=True)
    type_name = Column(String(5), nullable=False)

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    food_id = Column(Integer, ForeignKey('food_list.id'), nullable=False)
    meal_type_id = Column(Integer, ForeignKey('meal_type.id'), nullable=False)
    image_url = Column(String(255), nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    created_at = Column(DateTime,  default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class Total_Today(Base):
    __tablename__ = 'total_today'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    total_kcal = Column(Float, default=0, nullable=False)
    total_car = Column(Float, default=0, nullable=False)
    total_prot = Column(Float, default=0, nullable=False)
    total_fat = Column(Float, default=0, nullable=False)
    condition =Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    history_ids = Column(ARRAY(Integer), default=lambda: [], nullable=False)  # 빈 리스트 초기화


