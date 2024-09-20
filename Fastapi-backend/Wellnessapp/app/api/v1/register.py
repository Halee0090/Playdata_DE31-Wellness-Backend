from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from db import crud
from db.crud import calculate_age, get_user_by_email
from db.session import get_db
from db.models import Auth, User
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from schemas.user import UserCreate
import logging
import pytz


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

# 한국 표준시 (KST) 타임존 설정
KST = pytz.timezone('Asia/Seoul')

# UTC 시간을 KST로 변환
def get_kst_time():
    utc_time = datetime.utcnow()
    kst_time = utc_time.astimezone(KST)
    return kst_time

# 날짜 및 시간 형식을 'YYYY-MM-DD HH:MM:SS'로 포맷
def format_datetime(dt: datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Access 토큰 생성
def create_access_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access Token 생성 완료: {token}")
    return token

# 리프레시 토큰 생성
def create_refresh_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_delta)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Refresh Token 생성 완료: {token}")
    return token

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    existing_user = crud.get_user_by_email(db, email=user.email)
    if existing_user:
        return {
            "status": "Bad Request",
            "status_code": 400,
            "detail": "Email already registered"
        }

    # 키와 몸무게가 0보다 큰지 확인
    if user.height <= 0 or user.weight <= 0:
        logger.error("키와 몸무게가 잘못된 값입니다.")
        raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.") 
    
    # 성별을 "남성" -> 0, "여성" -> 1로 변환
    if user.gender == "남성":
        gender_value = 0
    elif user.gender == "여성":
        gender_value = 1
    else:
        raise HTTPException(status_code=400, detail="잘못된 성별 정보입니다.")
    
    # 생년월일로 나이를 계산
    user_age = calculate_age(user.birthday)
    
    try:        
        new_user = crud.create_user(db=db, user=user, age=user_age, gender=gender_value)

        
        # 권장 영양소 계산 및 저장
        recommendation = crud.calculate_and_save_recommendation(db, new_user)
        db.add(recommendation)
        db.flush()  # 이 시점에서 recommendation에 id가 할당
        
        logger.info(f"User weight: {user.weight}, height: {user.height}, age: {user_age}, gender: {gender_value}")
        
        # total_today 생성
        today = date.today()
        total_today = crud.create_total_today(db, new_user.id, today)
    
        db.commit()
        db.refresh(recommendation)
        db.refresh(new_user)
        db.refresh(total_today)
        
    except HTTPException as e:
        db.rollback()
        if new_user:
            logger.info(f"Creating total_today for user: {new_user.id} on date: {today}")
        return {
            "status": "Error",
            "status_code": e.status_code,
            "detail": f"Failed to create user: {str(e.detail)}"
        }


    # JWT 발행
    access_token = create_access_token(
                    data={"user_id": new_user.id, "user_email": new_user.email},
                    expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
                )
    refresh_token = create_refresh_token(
                    data={"user_id": new_user.id, "user_email": new_user.email},
                    expires_delta=REFRESH_TOKEN_EXPIRE_DAYS
                )

    # auth 테이블에 새 토큰 저장
    new_user_auth_entry = Auth(
                        user_id=new_user.id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        access_created_at=format_datetime(get_kst_time()),
                        access_expired_at=format_datetime(
                        get_kst_time() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                        ),
                        refresh_created_at=format_datetime(get_kst_time()),
                        refresh_expired_at=format_datetime(
                        get_kst_time() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
                            ),
                     )
    db.add(new_user_auth_entry)
    db.commit()
    
    return {
        "status": "success",
        "status_code": 201,
        "detail": {
            "wellness_info": {
                "access_token": access_token,
                "token_type": "bearer",
                "user_email": new_user.email,
                "user_nickname": new_user.nickname

            }
         },
        "message": "Registration is complete."
    }
