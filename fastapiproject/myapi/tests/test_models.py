import pytest
from sqlalchemy.orm import Session
from app.models import User, Recommend, Food_List, Meal_Type, History, Total_Today
from app.database import get_db
from datetime import datetime

@pytest.fixture
def db():
    return next(get_db())

def test_user_model(db: Session):
    user = User(
        nickname="TestUser",
        email="test@example.com",
        age=30,
        gender=1,
        height=175.0,
        weight=70.0,
        birthday=datetime(1990, 1, 1),
    )
    db.add(user)
    db.commit()

    queried_user = db.query(User).filter_by(email="test@example.com").first()
    assert queried_user is not None
    assert queried_user.nickname == "TestUser"
    assert queried_user.age == 30

    db.delete(queried_user)
    db.commit()

def test_recommend_model(db: Session):
    user = User(
        nickname="TestUser",
        email="test@example.com",
        age=30,
        gender=1,
        height=175.0,
        weight=70.0,
        birthday=datetime(1990, 1, 1),
    )
    db.add(user)
    db.commit()

    recommend = Recommend(
        user_id=user.id,
        rec_kcal=2000.0,
        rec_car=250.0,
        rec_prot=150.0,
        rec_fat=66.0,
    )
    db.add(recommend)
    db.commit()

    queried_recommend = db.query(Recommend).filter_by(user_id=user.id).first()
    assert queried_recommend is not None
    assert queried_recommend.rec_kcal == 2000.0
    assert queried_recommend.rec_car == 250.0

    db.delete(recommend)
    db.delete(user)
    db.commit()

# 다른 모델들에 대한 테스트도 유사한 방식으로 작성할 수 있습니다.