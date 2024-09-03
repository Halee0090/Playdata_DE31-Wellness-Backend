import pytest
from sqlalchemy.orm import Session
from app.crud import create_or_update_recommend, get_recommend_by_user_id
from app.models import User, Recommend
from app.database import get_db
from datetime import datetime, timedelta

@pytest.fixture
def db():
    return next(get_db())

@pytest.fixture
def sample_user(db: Session):
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
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()

def test_create_recommend(db: Session, sample_user: User):
    recommend = create_or_update_recommend(db, sample_user.id, 2000, 250, 150, 66)
    
    assert recommend.user_id == sample_user.id
    assert recommend.rec_kcal == 2000
    assert recommend.rec_car == 250
    assert recommend.rec_prot == 150
    assert recommend.rec_fat == 66

def test_update_recommend(db: Session, sample_user: User):
    # 첫 번째 추천 생성
    first_recommend = create_or_update_recommend(db, sample_user.id, 2000, 250, 150, 66)
    
    # 사용자 정보 업데이트
    sample_user.weight = 75.0
    sample_user.updated_at = datetime.now()
    db.commit()
    
    # 두 번째 추천 업데이트
    second_recommend = create_or_update_recommend(db, sample_user.id, 2200, 275, 165, 73)
    
    assert first_recommend.id == second_recommend.id  # 같은 레코드가 업데이트되었는지 확인
    assert second_recommend.rec_kcal == 2200
    assert second_recommend.updated_at > first_recommend.updated_at

def test_get_recommend_by_user_id(db: Session, sample_user: User):
    created_recommend = create_or_update_recommend(db, sample_user.id, 2000, 250, 150, 66)
    fetched_recommend = get_recommend_by_user_id(db, sample_user.id)
    
    assert fetched_recommend is not None
    assert fetched_recommend.id == created_recommend.id
    assert fetched_recommend.rec_kcal == 2000