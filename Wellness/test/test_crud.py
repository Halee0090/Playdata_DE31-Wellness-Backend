from app.crud import get_food_by_category, get_recommend_by_user
from app.models import FoodList, Recommend, Userinfo

def test_get_recommend_by_user(db_session):
    # 먼저 Userinfo 테이블에 사용자를 추가합니다.
    user = Userinfo(
        id=None,
        age=30,
        gender=1,
        height=175.5,
        weight=70.0,
        birthday="1990-01-01",
        email="test@test.com",
        nickname="testuser"
    )
    db_session.add(user)
    db_session.commit()
    
    recommend = Recommend(user_id=1, rec_kcal=2001, rec_car=300, rec_prot=100, rec_fat=50)
    db_session.add(recommend)
    db_session.commit()

    result = get_recommend_by_user(db_session, user_id=1)
    assert result is not None
    assert result.rec_kcal == 2001
    assert result.rec_car == 300
    assert result.rec_prot == 100
    assert result.rec_fat == 50


def test_get_food_by_category(db_session):
    food_item = FoodList(category_id=1, category_name="한식", food_name="비빔밥", food_kcal=500.0, food_car=80.0, food_prot=20.0, food_fat=10.0)
    db_session.add(food_item)
    db_session.commit()

    result = get_food_by_category(db_session, category_id=1)
    assert result is not None
    assert result.food_name == "비빔밥"
    assert result.food_kcal == 500.0
    assert result.food_car == 80.0
    assert result.food_prot == 20.0
    assert result.food_fat == 10.0
