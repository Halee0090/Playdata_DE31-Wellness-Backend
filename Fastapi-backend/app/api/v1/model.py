# /app/api/v1/model.py
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.crud import get_food_by_category, get_recommend_by_user
from app.utils.image_processing import extract_exif_data, determine_meal_type
from app.utils.s3 import upload_image_to_s3
import requests
from io import BytesIO
import os
import uuid

router = APIRouter()

@router.post("/predict")
async def classify_image(
    file: UploadFile = File(...), 
    user_id: int = Query(...),
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
        meal_type = determine_meal_type(date) if date else "기타"

        model_api_url = "http://localhost:8001/predict_url/"
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
        
        recommend = get_recommend_by_user(db, user_id)
        if not recommend:
            raise HTTPException(status_code=404, detail="User not found")

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
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
