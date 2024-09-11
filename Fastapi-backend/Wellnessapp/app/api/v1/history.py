from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.crud import create_history
from datetime import datetime
from db.models import History
from schemas.history import HistoryCreateRequest

router = APIRouter()

@router.post("/save_and_get")
def save_to_history_and_get_today_history(
    history_data: HistoryCreateRequest,  # Body로 데이터를 받음
    db: Session = Depends(get_db)
):
    try:
        # 1. 새 기록을 데이터베이스에 저장
        new_history = create_history(
            db=db,
            user_id=history_data.user_id,
            category_id=history_data.category_id,
            meal_type_id=history_data.meal_type_id,
            image_url=history_data.image_url,
            date=history_data.date
        )
        db.commit()  # 저장 완료

        # 2. 저장된 기록을 바로 반환
        response_data = {
            "history_id": new_history.id,  # 기록 ID
            "category_id": new_history.category_id,  # 카테고리 ID
            "meal_type_id": new_history.meal_type_id,  # 식사 유형 ID
            "created_at": new_history.created_at  # 생성된 시간
        }

        return {
            "status": "success",
            "status_code": 201,
            "detail": response_data,  # 저장된 기록 반환
            "message": "History saved successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")
