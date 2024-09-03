from sqlalchemy import ForeignKey, Column, Integer, String, Float, DECIMAL, DateTime, TIMESTAMP, DATE, Boolean, ARRAY
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base



class User(Base):
    __tablename__ = 'user_info'

    id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)
    height = Column(DECIMAL(4, 1), nullable=False)
    weight = Column(DECIMAL(4, 1), nullable=False)
    birthday = Column(DATE, nullable=False)
    email = Column(String(100), nullable=False)
    nickname = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

class Recommend(Base):
    __tablename__ = 'recommend'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    rec_kcal = Column(DECIMAL(6, 2), nullable=False)
    rec_car = Column(DECIMAL(6, 2), nullable=False)
    rec_prot = Column(DECIMAL(6, 2), nullable=False)
    rec_fat = Column(DECIMAL(6, 2), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)

class Food_List(Base):
    __tablename__ = 'food_list'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, nullable=False)
    food_name = Column(String(15), nullable=False)
    category_name = Column(String(10), nullable=False)
    food_kcal = Column(DECIMAL(5, 2), nullable=False)
    food_car = Column(DECIMAL(5, 2), nullable=False)
    food_prot = Column(DECIMAL(5, 2), nullable=False)
    food_fat = Column(DECIMAL(5, 2), nullable=False)


class Meal_Type(Base):
    __tablename__ = 'meal_type'
    id = Column(Integer, primary_key=True)
    type_name = Column(String(5), nullable=False)

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    food_id = Column(Integer, ForeignKey('food_list.id'), nullable=False)
    meal_type_id = Column(Integer, ForeignKey('meal_type.id'), nullable=False)
    image_url = Column(String(255), nullable=False)
    date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)

class Total_Today(Base):
    __tablename__ = 'total_today'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    total_kcal = Column(DECIMAL(6, 2), nullable=False)
    total_car = Column(DECIMAL(6, 2), nullable=False)
    total_prot = Column(DECIMAL(6, 2), nullable=False)
    total_fat = Column(DECIMAL(6, 2), nullable=False)
    condition = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)
    today = Column(DATE, nullable=False)
    history_ids = Column(ARRAY(Integer), nullable=False)
