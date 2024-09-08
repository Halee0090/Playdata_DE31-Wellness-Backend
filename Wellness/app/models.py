from sqlalchemy import Column, Integer, DECIMAL, DATE, VARCHAR, TIMESTAMP, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from app.database import Base

class FoodList(Base):
    __tablename__ = "food_list"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, unique=True, nullable=False)
    category_name = Column(VARCHAR(10), nullable=False)  # 'character varying' 대신 'String' 사용
    food_name = Column(VARCHAR(5), nullable=False)  # 'character varying' 대신 'String' 사용
    food_kcal = Column(DECIMAL(6,2), nullable=False)
    food_car = Column(DECIMAL(6,2), nullable=False)
    food_prot = Column(DECIMAL(6,2), nullable=False)
    food_fat = Column(DECIMAL(6,2), nullable=False)
    
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