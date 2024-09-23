from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt
from schemas.user import UserCreate
from db import crud
from db.crud import calculate_age, get_user_by_email
from db.session import get_db
from db.models import Auth, User
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import logging
import pytz  
from fastapi.responses import JSONResponse
from services.auth_service import create_access_token, create_refresh_token


# .env 파일 로드
load_dotenv()

# 환경 변수 설정
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# KST 타임존 설정
KST = pytz.timezone('Asia/Seoul')

# 날짜 및 시간 형식을 'YYYY-MM-DD HH:MM:SS'로 포맷
def format_datetime(dt: datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # 이메일 중복 확인
        existing_user = crud.get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
            
        # 생년월일이 현재 연도와 같은지 확인
        current_year = datetime.now().year
        if user.birthday.year == current_year:
            return JSONResponse(
                content={
                    "status": "Bad Request",
                    "status_code": 400,
                    "detail": "Birthday cannot be the current year."
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            
        # 성별 변환
        if user.gender == "남성":
            gender_value = 0
        elif user.gender == "여성":
            gender_value = 1
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid gender information."
            )

        # 생년월일로 나이를 계산
        user_age = calculate_age(user.birthday)
        
        # 사용자 생성
        new_user = crud.create_user(db=db, user=user, age=user_age, gender=gender_value)

        # 권장 영양소 계산 및 저장
        recommendation = crud.calculate_and_save_recommendation(db, new_user)
        db.add(recommendation)
        
        # total_today 생성
        today = date.today()
        total_today = crud.create_total_today(db, new_user.id, today)

        # JWT 토큰 생성
        access_token = create_access_token(
            data={"user_id": new_user.id, "user_email": new_user.email},
            expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token = create_refresh_token(
            data={"dummy": "dummy_value"}, 
            expires_delta=REFRESH_TOKEN_EXPIRE_DAYS
        )

        # 토큰 정보 저장
        new_user_auth_entry = Auth(
            user_id=new_user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_created_at=format_datetime(datetime.now(KST)),
            access_expired_at=format_datetime(datetime.now(KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
            refresh_created_at=format_datetime(datetime.now(KST)),
            refresh_expired_at=format_datetime(datetime.now(KST) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
            )
        db.add(new_user_auth_entry)
        db.commit()

        return {
            "status": "success",
            "status_code": 201,
            "detail": {
                "wellness_info": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "user_email": new_user.email,
                    "user_nickname": new_user.nickname.encode('utf-8').decode('utf-8'),
                    "user_birthday": new_user.birthday,
                    "user_age": user_age,
                    "user_gender": gender_value,
                    "user_height": new_user.height,
                    "user_weight": new_user.weight
                }
            },
            "message": "Registration is complete"
        }

    except (SQLAlchemyError, HTTPException) as e:
        db.rollback()  # 오류 발생 시 롤백
        logger.error(f"Failed to create user: {str(e)}")
        return JSONResponse(
            content={
                "status": "Error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": f"Failed to create user: {str(e)}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    except Exception as e:
        db.rollback()  # 예상치 못한 오류에도 롤백 수행
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            content={
                "status": "Error",
                "status_code": 500,
                "detail": f"Unexpected error: {str(e)}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )