import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app, get_db
from app.models import User, Recommend, Total_Today
from datetime import date
from decimal import Decimal

# 테스트 데이터베이스 URL 설정
TEST_DATABASE_URL = "postgresql://wellness:wellness123@localhost:5432/test_wellness_db"

# 테스트용 SQLAlchemy 엔진 생성
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

def test_recommend_nutrition_existing_user(client, db_session):
    # 기존 사용자 삭제 (있다면)
    db_session.query(User).filter(User.id == 1).delete()
    db_session.commit()

    # 테스트용 사용자 추가
    user = User(
        id=1,
        age=30,
        gender=1,
        height=Decimal('175.0'),
        weight=Decimal('70.0'),
        birthday=date(1994, 1, 1),
        email="test@example.com",
        nickname="test_user"
    )
    db_session.add(user)
    db_session.commit()

    # 권장 영양소 추가
    recommend = Recommend(
        user_id=1,
        rec_kcal=Decimal('2000.00'),
        rec_car=Decimal('250.00'),
        rec_prot=Decimal('75.00'),
        rec_fat=Decimal('66.00')
    )
    db_session.add(recommend)
    db_session.commit()

    response = client.get("/recommend/eaten_nutrient", params={"user_id": 1, "date": "2024-09-06"})
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "total_kcal": Decimal('0.00'),
        "total_car": Decimal('0.00'),
        "total_prot": Decimal('0.00'),
        "total_fat": Decimal('0.00'),
        "rec_kcal": Decimal('2000.00'),
        "rec_car": Decimal('250.00'),
        "rec_prot": Decimal('75.00'),
        "rec_fat": Decimal('66.00'),
        "condition": False
    }

def test_recommend_nutrition_invalid_user(client):
    response = client.get("/recommend/eaten_nutrient", params={"user_id": 9999, "date": "2024-09-06"})

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

def test_recommend_nutrition_invalid_date_format(client, db_session):
    # 유효한 사용자 생성
    user = User(
        id=2,
        age=25,
        gender=2,
        height=Decimal('160.0'),
        weight=Decimal('55.0'),
        birthday=date(1999, 5, 15),
        email="test2@example.com",
        nickname="test_user2"
    )
    db_session.add(user)
    db_session.commit()

    response = client.get("/recommend/eaten_nutrient", params={"user_id": 2, "date": "2024/09/06"})  # 잘못된 날짜 형식

    assert response.status_code == 422
    data = response.json()
    
    assert any(
        error['msg'] == "String should match pattern '^\\d{4}-\\d{2}-\\d{2}$'"
        for error in data['detail']
    )
