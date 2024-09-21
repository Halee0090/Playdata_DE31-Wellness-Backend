# /app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator, Generator
from core.config import DATABASE_URL, TEST_DATABASE_URL
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# SQLAlchemy 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)



# Base 클래스 생성
Base = declarative_base()

# DB 연결 세션 함수
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

async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)