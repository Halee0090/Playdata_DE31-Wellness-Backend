# /app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from core.config import DATABASE_URL, TEST_DATABASE_URL  # config.py에서 환경 변수 가져오기
from pytz import timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator, Generator
import os
from dotenv import load_dotenv

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, connect_args={'options': '-c timezone=Asia/Seoul'})
test_engine = create_engine(TEST_DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Base 클래스 생성
Base = declarative_base()

# 모델 정의를 데이터베이스에 반영합니다.
Base.metadata.create_all(engine)

# DB 연결 세션 함수
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test DB 연결 세션 함수
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
    Base.metadata.create_all(bind=test_engine)



# SQLAlchemy 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

#DB 연결 세션 함수
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# async_session 이름으로 함수 추가
async_session = AsyncSessionLocal

# 동기 DB 연결 세션 함수
def get_db() -> Generator[AsyncSession, None, None]:
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        session.close()

# 테이블 생성 (비동기)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
