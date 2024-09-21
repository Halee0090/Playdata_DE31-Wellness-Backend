from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from jose import jwt, JWTError
from schemas.user import UserLogin
from db.session import get_db
from db.models import Auth, User
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
<<<<<<< HEAD
=======
import pytz  
from pytz import UTC
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93

# .env 파일 로드
load_dotenv()

# 환경 변수 로드
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

<<<<<<< HEAD
=======
# KST 타임존 설정
KST = pytz.timezone('Asia/Seoul')

>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
# 날짜 및 시간 형식을 'YYYY-MM-DD HH:MM:SS'로 포맷
def format_datetime(dt: datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Access 토큰 생성
def create_access_token(data: dict, expires_delta: int):
    to_encode = data.copy()
<<<<<<< HEAD
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
=======
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)  # UTC 시간 사용
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access Token 생성 완료: {token}")
    return token

# 리프레시 토큰 생성
def create_refresh_token(data: dict, expires_delta: int):
    to_encode = data.copy()
<<<<<<< HEAD
    expire = datetime.utcnow() + timedelta(days=expires_delta)
=======
    expire = datetime.utcnow() + timedelta(days=expires_delta)  # UTC 시간 사용
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Refresh Token 생성 완료: {token}")
    return token

# 엑세스 토큰 만료 확인 함수
def is_access_token_expired(expiry_time: datetime):
<<<<<<< HEAD
    return datetime.utcnow() > expiry_time

# 토큰 검증 함수
def verify_refresh_token(token: str, expiry_time: datetime):
    if datetime.utcnow() > expiry_time:
=======
    return datetime.utcnow() > expiry_time  # UTC 시간 기준

# 토큰 검증 함수
def verify_refresh_token(token: str, expiry_time: datetime):
    current_time_utc = datetime.now(pytz.UTC).replace(tzinfo=UTC)  # UTC 시간으로 변환
    
    if expiry_time.tzinfo is None:  
        expiry_time = expiry_time.replace(tzinfo=UTC)
        
    if current_time_utc > expiry_time:
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
        logger.error("Refresh token expired based on expiry_time in DB")
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Refresh Token validated successfully: {payload}")
        return payload
    except JWTError as e:   
        logger.error(f"Refresh token validation failed: {e}")
        raise HTTPException(
            status_code=401, detail="Refresh token invalid or expired")

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"로그인 시도: {user.email}, {user.nickname}")

    # 사용자 확인
    db_user = db.query(User).filter(User.email == user.email).first()
<<<<<<< HEAD
    if db_user:
        logger.info(f"DB User found: {db_user.email}, ID: {db_user.id}")
    else:
=======
    if not db_user:
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
        logger.error(f"DB User not found: {user.email}")
        raise HTTPException(status_code=400, detail="User not found")

    # auth 테이블에서 사용자 토큰 확인
    auth_entry = db.query(Auth).filter(Auth.user_id == db_user.id).first()

    if auth_entry:
        # 엑세스 토큰 만료 확인
        if is_access_token_expired(auth_entry.access_expired_at):
<<<<<<< HEAD
            try:
                # refresh 토큰 검증
                verify_refresh_token(auth_entry.refresh_token, auth_entry.refresh_expired_at)
=======
            logger.info("Access token has expired. Checking refresh token.")
            try:
                # refresh 토큰 검증
                verify_refresh_token(auth_entry.refresh_token, auth_entry.refresh_expired_at)
                logger.info("Refresh token is valid. Issuing new access token.")
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93

                # refresh 토큰이 유효하므로 access 토큰만 재발급
                access_token = create_access_token(
                    data={"user_id": db_user.id, "user_email": db_user.email},
                    expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
                )
                auth_entry.access_token = access_token
<<<<<<< HEAD
                auth_entry.access_created_at = format_datetime(datetime.utcnow())
                auth_entry.access_expired_at = format_datetime(
                    datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                )
                logger.info(f"access_created_at: {auth_entry.access_created_at}, access_expired_at: {auth_entry.access_expired_at}")
                
                try:
                    db.commit()
                    
=======
                auth_entry.access_created_at = format_datetime(datetime.now(KST))  # KST 시간으로 변환
                auth_entry.access_expired_at = format_datetime(
                    (datetime.now(KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).replace(tzinfo=pytz.UTC)
                )

                try:
                    db.commit()
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                except SQLAlchemyError as e:
                    db.rollback()
                    logger.error(f"failed to commit to DB: {e}")
                    raise HTTPException(status_code=500, detail="Failed to issue new token")
<<<<<<< HEAD
                    
=======

>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                return {
                    "status": "success",
                    "status_code": 200,
                    "detail": {
                        "wellness_info": {
                            "access_token": auth_entry.access_token,
                            "refresh_token": auth_entry.refresh_token,  # refresh 토큰은 유지
                            "token_type": "bearer",
                            "user_email": db_user.email,
<<<<<<< HEAD
                            "user_nickname": db_user.nickname,
                            "user_birthday": db_user.birthday,
                            "user_gender": db_user.gender,
                            "user_height": db_user.height,
                            "user_weight": db_user.weight,
                            "user_age": db_user.age,
=======
                            "user_nickname": db_user.nickname.encode('utf-8').decode('utf-8')
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                        }
                    },
                    "message": "Access token renewed."
                }

<<<<<<< HEAD
            except HTTPException:
=======
            except HTTPException as e:
                logger.info("Refresh token has expired. Issuing new tokens.")
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                # 엑세스 토큰과 리프레시 토큰이 모두 만료된 경우 새로 발급
                access_token = create_access_token(
                    data={"user_id": db_user.id, "user_email": db_user.email},
                    expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
                )
                refresh_token = create_refresh_token(
                    data={"user_id": db_user.id, "user_email": db_user.email},
                    expires_delta=REFRESH_TOKEN_EXPIRE_DAYS
                )

<<<<<<< HEAD
                # auth 테이블에 새 토큰 저장
                new_auth_entry = Auth(
                    user_id=db_user.id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    access_created_at=format_datetime(datetime.utcnow()),
                    access_expired_at=format_datetime(
                        datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    ),
                    refresh_created_at=format_datetime(datetime.utcnow()),
                    refresh_expired_at=format_datetime(
                        datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
                    ),
                )
                db.add(new_auth_entry)
                db.commit()

                logger.info(f"Committing new auth entry for user_id {db_user.id}")
=======
                # 기존 auth_entry를 업데이트 (새로 생성하지 않음)
                auth_entry.access_token = access_token
                auth_entry.refresh_token = refresh_token
                auth_entry.access_created_at = format_datetime(datetime.now(KST))  # KST 시간으로 변환
                auth_entry.access_expired_at = format_datetime(
                    (datetime.now(KST) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).replace(tzinfo=pytz.UTC)
                )
                auth_entry.refresh_created_at = format_datetime(datetime.now(KST))  # KST 시간으로 변환
                auth_entry.refresh_expired_at = format_datetime(
                    (datetime.now(KST) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=pytz.UTC)

                )

                try:
                    db.commit()
                except SQLAlchemyError as e:
                    db.rollback()
                    logger.error(f"failed to commit to DB: {e}")
                    raise HTTPException(status_code=500, detail="Failed to issue new token")

                logger.info(f"Updated auth entry for user_id {db_user.id}")
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                return {
                    "status": "success",
                    "status_code": 201,
                    "detail": {
                        "wellness_info": {
<<<<<<< HEAD
                            "access_token": new_auth_entry.access_token,
                            "refresh_token": new_auth_entry.refresh_token,
                            "token_type": "bearer",
                            "user_email": db_user.email,
                            "user_nickname": db_user.nickname,
                            "user_birthday": db_user.birthday,
                            "user_gender": db_user.gender,
                            "user_height": db_user.height,
                            "user_weight": db_user.weight,
                            "user_age": db_user.age,
=======
                            "access_token": auth_entry.access_token,
                            "refresh_token": auth_entry.refresh_token,
                            "token_type": "bearer",
                            "user_email": db_user.email,
                            "user_nickname": db_user.nickname.encode('utf-8').decode('utf-8')
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                        }
                    },
                    "message": "New access and refresh tokens issued."
                }

        else:
            # 엑세스 토큰이 아직 유효한 경우
            logger.info(f"Valid access token found for user_id: {db_user.id}")
            return {
                "status": "success",
                "status_code": 200,
                "detail": {
                    "wellness_info": {
                        "access_token": auth_entry.access_token,
                        "refresh_token": auth_entry.refresh_token,
                        "token_type": "bearer",
                        "user_email": db_user.email,
<<<<<<< HEAD
                        "user_nickname": db_user.nickname,
                        "user_birthday": db_user.birthday,
                        "user_gender": db_user.gender,
                        "user_height": db_user.height,
                        "user_weight": db_user.weight,
                        "user_age": db_user.age,
=======
                        "user_nickname": db_user.nickname.encode('utf-8').decode('utf-8')
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
                    }
                },
                "message": "Existing token provided."
            }

    else:
        logger.error(f"No auth entry found for user_id: {db_user.id}")
<<<<<<< HEAD
        raise HTTPException(status_code=400, detail="No auth entry found.")
=======
        raise HTTPException(status_code=400, detail="No auth entry found.")
>>>>>>> fea0b14d5412fc76acd48640aeff5a47ef0e6e93
