from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app import models
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator

# 데이터베이스 URL 설정 
URL_DATABASE = "postgresql+psycopg2://wellness:wellness123@localhost:5432/wellness_db"

# SQLAlchemy 엔진 생성
engine = create_engine(URL_DATABASE)
# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # Base 클래스 생성

#database에 대한 연결
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
        
# 테이블 생성
Base.metadata.create_all(bind=engine)