import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from sqlalchemy.orm import Session, declarative_base
from typing import Generator
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 URL 설정 
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)
test_engine = create_engine(TEST_DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base()  # Base 클래스 생성
TestBase = declarative_base()

#database에 대한 연결
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

def get_test_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 테이블 생성
def init_db():
    Base.metadata.create_all(bind=engine)


def init_test_db():
    TestBase.metadata.create_all(bind=test_engine)