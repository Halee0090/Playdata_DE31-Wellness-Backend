import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import Base, get_db
from app.main import app

# PostgreSQL 데이터베이스 URL (테스트용 데이터베이스를 사용하세요)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:playdata123@localhost/test_db"


# PostgreSQL용 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI 테스트 클라이언트 fixture
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# DB 세션 fixture
@pytest.fixture(scope="function")
def db_session():
    # 테스트용 DB 초기화
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# FastAPI 클라이언트와 DB 의존성 오버라이드
@pytest.fixture(scope="function")
def client_with_db(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
