import pytest
from sqlalchemy.orm import Session
from app.recommend import recommend_nutrition
from app.models import User, Recommend
from app.database import get_db
from datetime import datetime, timedelta
from fastapi import HTTPException

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

def test_recommend_nutrition_new_user(db: Session, sample_user: User):
    result = recommend_nutrition(sample_user.id, db)
    
    assert result["status"] == "success"
    assert "rec_kcal" in result
    assert "rec_car" in result
    assert "rec_prot" in result
    assert "rec_fat" in result
    assert "last_updated" in result

def test_recommend_nutrition_existing_user(db: Session, sample_user: User):
    # 첫 번째 추천 생성
    first_result = recommend_nutrition(sample_user.id, db)
    
    # 사용자 정보 업데이트
    sample_user.weight = 75.0
    sample_user.updated_at = datetime.now()
    db.commit()
    
    # 두 번째 추천 요청
    second_result = recommend_nutrition(sample_user.id, db)
    
    assert first_result["rec_kcal"] != second_result["rec_kcal"]
    assert first_result["last_updated"] < second_result["last_updated"]

def test_recommend_nutrition_invalid_user(db: Session):
    with pytest.raises(HTTPException) as excinfo:
        recommend_nutrition(999, db)  # 존재하지 않는 사용자 ID
    
    assert excinfo.value.status_code == 400
    assert "Invalid user_id" in str(excinfo.value.detail)





def test_recommend_nutrition_rounding(db: Session, sample_user: User):
    # recommend_nutrition 함수 호출
    result = recommend_nutrition(sample_user.id, db)

    # 결과값이 소수점 둘째자리까지 반올림되었는지 확인
    assert round(result["rec_kcal"], 2) == result["rec_kcal"]
    assert round(result["rec_car"], 2) == result["rec_car"]
    assert round(result["rec_prot"], 2) == result["rec_prot"]
    assert round(result["rec_fat"], 2) == result["rec_fat"]

    # 데이터베이스에 저장된 값 확인
    stored_recommend = db.query(Recommend).filter(Recommend.user_id == sample_user.id).first()
    assert stored_recommend is not None

    # 데이터베이스에 저장된 값이 소수점 둘째자리까지 반올림되었는지 확인
    assert round(stored_recommend.rec_kcal, 2) == stored_recommend.rec_kcal
    assert round(stored_recommend.rec_car, 2) == stored_recommend.rec_car
    assert round(stored_recommend.rec_prot, 2) == stored_recommend.rec_prot
    assert round(stored_recommend.rec_fat, 2) == stored_recommend.rec_fat

    # 함수 반환값과 데이터베이스 저장값이 일치하는지 확인
    assert result["rec_kcal"] == stored_recommend.rec_kcal
    assert result["rec_car"] == stored_recommend.rec_car
    assert result["rec_prot"] == stored_recommend.rec_prot
    assert result["rec_fat"] == stored_recommend.rec_fat

    # 추가로, 반올림이 정확히 이루어졌는지 확인하기 위해 
    # 예상되는 값과 비교할 수 있습니다. (이 부분은 실제 계산 로직에 따라 조정이 필요합니다)
    expected_kcal = 2447.77  # 예시 값
    assert abs(result["rec_kcal"] - expected_kcal) < 0.01