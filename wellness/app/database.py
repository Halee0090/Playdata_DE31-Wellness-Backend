import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# .env 파일 로드(환경변수 설정)
load_dotenv()

# postgresql 데이터베이스 url을 환경변수로부터 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# 엔진 및 세션 초기화
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 정의
Base = declarative_base()

# 의존성 주입용 함수 (DB 세션 관리)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()