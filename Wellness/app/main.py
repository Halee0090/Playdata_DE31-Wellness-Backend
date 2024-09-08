import datetime
import logging
import requests  
from fastapi import FastAPI, Query, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.s3 import upload_image_to_s3
from app.crud import get_food_by_category, get_recommend_by_user
from PIL import Image, ExifTags
import uuid
import uvicorn
from io import BytesIO
import datetime
import os


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def extract_exif_data(file_bytes: bytes):
    """이미지에서 EXIF 데이터 추출하는 함수"""
    try:
        img = Image.open(BytesIO(file_bytes))
        exif_data = img._getexif()
        if not exif_data:
            return None
        
        for tag, value in exif_data.items():
            if ExifTags.TAGS.get(tag, tag) == "DateTimeOriginal":
                return value  # 예: '2022:03:15 10:20:35'
        return None
    
    except Exception as e:
        logger.error(f"Error extracting Exif data: {str(e)}")
        return None
    
        
def determine_meal_type(taken_time: str) -> str:
    """촬영 시간에 따른 meal_type 결정"""
    try:
        time_format = "%Y:%m:%d %H:%M:%S"
        taken_time_obj = datetime.datetime.strptime(taken_time, time_format)
        hour = taken_time_obj.hour

        if 6 <= hour <= 8:
            return "아침"
        elif 11 <= hour <= 13:
            return "점심"
        elif 17 <= hour <= 19:
            return "저녁"
        else:
            return "기타"
    except Exception as e:
        logger.error(f"Error determining meal type: {str(e)}")
        return "기타"
        
@app.post("/api/v1/model/predict")
async def classify_image(
    file: UploadFile = File(...), 
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    try:
        # 메모리에서 파일 읽기
        file_bytes = await file.read()
        file_extension = file.filename.split(".")[-1]
        unique_file_name = f"{uuid.uuid4()}.{file_extension}"

        # .env 파일에서 bucket_name 가져오기
        bucket_name =  os.getenv("BUCKET_NAME", "default_bucket_name")
        
        # 이미지 s3에 업로드
        try:
            image_url = upload_image_to_s3(BytesIO(file_bytes), bucket_name, unique_file_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to upload image to s3: {str(e)}")
        
         # EXIF에서 촬영 날짜 추출
        date = extract_exif_data(file_bytes)
        meal_type = determine_meal_type(date) if date else "기타"

        # 모델에 분류 요청 (model_api.py의 /predict_url/에 요청)
        model_api_url = "http://localhost:8001/predict_url/"  # model_api 서버로 요청
        try:
            response = requests.post(model_api_url, params={"image_url": image_url})
            response.raise_for_status
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Model API request failed: {str(e)}")

        # 분류된 카테고리 ID 가져오기
        category_id = response.json().get("category_id")
        if category_id is None:
            raise HTTPException(status_code=400, detail="Category ID is required")

        # 분류된 결과로 음식 정보 조회
        food = get_food_by_category(db, category_id)
        if not food:
            raise HTTPException(status_code=404, detail="Food not found")
        
        # user_id로 권장량 정보 조회
        recommend = get_recommend_by_user(db, user_id)
        if not recommend:
            raise HTTPException(status_code=404, detail="user not found")

        # 결과 반환
        return {
            "status": "success",
            "date": date, 
            "meal_type": meal_type, 
            "category_id": category_id, 
            "food_name": food.category_name, 
            "food_kcal": food.food_kcal, 
            "food_car": round(food.food_car), 
            "food_prot": round(food.food_prot), 
            "food_fat": round(food.food_fat), 
            "rec_kcal": recommend.rec_kcal, 
            "rec_car": round(recommend.rec_car), 
            "rec_prot": round(recommend.rec_prot), 
            "rec_fat": round(recommend.rec_fat),
            "image_url": image_url
            }
    
    except HTTPException as e:
        logger.error(f"HTTP error occurred: {str(e)}")
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
