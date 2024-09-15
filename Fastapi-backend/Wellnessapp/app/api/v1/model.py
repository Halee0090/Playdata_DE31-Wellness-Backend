# /app/api/v1/model.py
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from api.v1.auth import validate_token
from db.session import get_db
from db.crud import get_food_by_category, get_recommend_by_user, get_recommend_by_user_id
from utils.image_processing import extract_exif_data, determine_meal_type
from utils.s3 import upload_image_to_s3
import requests
from io import BytesIO
import os
import uuid
import datetime
from fastapi.responses import JSONResponse
from decimal import Decimal
from db import models

router = APIRouter()

# Decimal 타입을 float으로 변환하는 함수
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@router.post("/predict")
async def classify_image(
    current_user: models.User = Depends(validate_token),  # 토큰 검증 추가
    file: UploadFile =  File(...), 
    db: Session = Depends(get_db)
):
    try:
        file_bytes = await file.read()
        file_extension = file.filename.split(".")[-1]
        unique_file_name = f"{uuid.uuid4()}.{file_extension}"
        bucket_name = os.getenv("BUCKET_NAME", "default_bucket_name")
        
        try:
            image_url = upload_image_to_s3(BytesIO(file_bytes), bucket_name, unique_file_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to upload image to s3: {str(e)}")
        
        date = extract_exif_data(file_bytes)
        if date is None:
            date = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")  # 현재 시간을 문자열로 설정
            
        meal_type = determine_meal_type(date) if date else "기타"

        model_api_url = "http://Wellnessmodel:8001/predict_url/"

        try:
            response = requests.post(model_api_url, params={"image_url": image_url})
            response.raise_for_status()
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Model API request failed: {str(e)}")

        category_id = response.json().get("category_id")
        if category_id is None:
            raise HTTPException(status_code=400, detail="Category ID is required")

        food = get_food_by_category(db, category_id)
        if not food:
            raise HTTPException(status_code=404, detail="Food not found")
        
        recommend = get_recommend_by_user(db, current_user.id)
        if not recommend:
            raise HTTPException(status_code=404, detail="User not found")
        
        # meal_type과 category_name을 UTF-8로 인코딩
        meal_type_utf8 = meal_type.encode('utf-8').decode('utf-8')
        category_name_utf8 = food.category_name.encode('utf-8').decode('utf-8')

        # UTF-8로 JSON 응답을 반환, Decimal을 float으로 변환
        return JSONResponse(
            content={
                "status": "success",
                "status_code": 201,
                "detail": {
                    "wellness_image_info": {
                        "date": date, 
                        "meal_type": meal_type_utf8,  # UTF-8 인코딩된 값 사용
                        "category_id": category_id, 
                        "category_name": category_name_utf8,  # UTF-8 인코딩된 값 사용
                        "food_kcal": decimal_to_float(food.food_kcal),  # Decimal을 float으로 변환
                        "food_car": round(float(food.food_car)), 
                        "food_prot": round(float(food.food_prot)), 
                        "food_fat": round(float(food.food_fat)), 
                        "rec_kcal": decimal_to_float(recommend.rec_kcal), 
                        "rec_car": round(float(recommend.rec_car)), 
                        "rec_prot": round(float(recommend.rec_prot)), 
                        "rec_fat": round(float(recommend.rec_fat)),
                        "image_url": image_url
                    }
                },
                "message": "Image Classify Information saved successfully"
            },
            media_type="application/json; charset=utf-8"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
