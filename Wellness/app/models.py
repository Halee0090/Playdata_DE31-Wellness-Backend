from sqlalchemy import ForeignKey, Column, Integer, String, Float, DECIMAL, DateTime, TIMESTAMP, DATE, Boolean, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

class FoodList(Base):
    __tablename__ = "food_list"

    
class Userinfo(Base):
    __tablename__ =  "user_info"
    
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(Integer, nullable=False)
    height = Column(DECIMAL(4,1), nullable=False)
    weight = Column(DECIMAL(4,1), nullable=False)
    birthday = Column(DATE, nullable=False)
    email = Column(VARCHAR(100), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    nickname = Column(VARCHAR(20), nullable=False)

    # 관계 설정: Recommend 클래스와의 연결
    recommendations = relationship("Recommend", back_populates="user")
    
class Recommend(Base):
    __tablename__ =  "recommend"
    
    id = Column(Integer, primary_key=True, index=True, default=0)
    user_id = Column(Integer, ForeignKey('user_info.id'), nullable=False)
    rec_kcal = Column(Integer, nullable=False)
    rec_car = Column(DECIMAL(6,2), nullable=False)
    rec_prot = Column(DECIMAL(6,2), nullable=False)
    rec_fat= Column(DECIMAL(6,2), nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # User와 관계 설정
    user = relationship("Userinfo", back_populates="recommendations")