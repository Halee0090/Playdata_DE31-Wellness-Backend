import pytest

@pytest.mark.asyncio
async def test_classify_image(client):
    # 테스트용 이미지 파일을 열어 업로드
    with open("test/test_image.jpeg", "rb") as img:
        response = client.post(
            "/api/v1/model/predict?user_id=1",
            files={"file": ("test_image.jpeg", img, "image/jpeg")}
        )
    # 상태 코드가 200인지 확인
    assert response.status_code == 200

    # 응답 데이터 확인
    json_data = response.json()
    assert json_data["status"] == "success"
    assert json_data["meal_type"] is not None
    assert json_data["category_id"] is not None
    assert json_data["food_name"] is not None
    assert json_data["food_kcal"] is not None
