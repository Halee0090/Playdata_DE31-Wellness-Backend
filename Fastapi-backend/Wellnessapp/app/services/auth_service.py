from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
import pytz
from pytz import UTC
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from db.session import get_db
from db.models import Auth, User
from schemas.auth import Token, TokenData
import logging
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 로드
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


# 토큰을 Bearer 방식으로 받아오는 OAuth2 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 로깅 설정
logger = logging.getLogger(__name__)

# Access 토큰 생성
def create_access_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)  # UTC 시간 사용
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access Token 생성 완료: {token}")
    return token

# 리프레시 토큰 생성
def create_refresh_token(data: dict, expires_delta: int):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_delta)  # UTC 시간 사용
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Refresh Token 생성 완료: {token}")
    return token

# 엑세스 토큰 만료 확인 함수
def is_access_token_expired(expiry_time: datetime) -> bool:
    current_time_utc = datetime.utcnow()  # 현재 UTC 시간
    return current_time_utc > expiry_time  # 만료 시간이 현재 시간보다 이전인지 확인


# 토큰 검증 함수
def verify_refresh_token(token: str, expiry_time: datetime):
    current_time_utc = datetime.now(pytz.UTC).replace(tzinfo=UTC)  # UTC 시간으로 변환
    
    if expiry_time.tzinfo is None:  
        expiry_time = expiry_time.replace(tzinfo=UTC)
        
    if current_time_utc > expiry_time:
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


async def validate_token(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # 토큰을 확인하는 로그 추가
    logger.info(f"Received token: {token}")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 데이터베이스에서 토큰 조회
    auth_entry = db.query(Auth).filter(Auth.access_token == token).first()
    
    if auth_entry is None:
        # 토큰 조회 실패 시 로그 기록
        logger.error(f"Token not found in the database: {token}")
        raise credentials_exception

    # 토큰 만료 여부 확인
    if auth_entry.access_expired_at < datetime.utcnow():
        # 만료된 토큰일 경우 로그 기록
        logger.error(f"Token expired: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 여기서 User 객체 반환
    user = db.query(User).filter(User.id == auth_entry.user_id).first()
    if user is None:
        logger.error(f"User not found for token: {token}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Returning user object: {user} of type {type(user)}")
    return user

