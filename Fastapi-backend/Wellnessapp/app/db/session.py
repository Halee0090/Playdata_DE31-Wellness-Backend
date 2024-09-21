# /app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
from core.config import DATABASE_URL, TEST_DATABASE_URL
import os
from sqlalchemy import event
from sqlalchemy.sql import text

DATABASE_URL = os.getenv("DATABASE_URL")
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# SQLAlchemy 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

@event.listens_for(engine.sync_engine, "connect")
def set_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"SET timezone TO '{TIMEZONE}'")
    cursor.close()
test_engine = create_async_engine(TEST_DATABASE_URL)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
AsyncTestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# Base 클래스 생성
Base = declarative_base()

# DB 연결 세션 함수
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Test DB 연결 세션 함수
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 테이블 생성
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)