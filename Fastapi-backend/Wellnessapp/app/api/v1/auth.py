from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from pytz import timezone
from sqlalchemy.orm import Session
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import APIRouter, Depends
from db.models import Auth
from db.session import get_db
from dotenv import load_dotenv
import os
import logging
from services.auth_service import create_access_token
from schemas.auth import TokenRequest

# .env 파일 로드
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# KST timezone 설정
KST = timezone('Asia/Seoul')

# 토큰 검증 및 재발급 API
@router.post("/verify")
async def verify_token(token_data: TokenRequest, db: Session = Depends(get_db)):
    access_token = token_data.access_token
    refresh_token = token_data.refresh_token
    
    logger.info(f"검증을 위해 받은 Access Token: {access_token}")
    
    try:
        # 엑세스 토큰 검증
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        logger.info(f"엑세스 토큰 유효, 유저 ID: {user_id}")
  
    except ExpiredSignatureError:
        logger.warning(f"엑세스 토큰 만료. 리프레시 토큰 확인 중: {refresh_token}")

        try:
            # 리프레시 토큰 검증 및 DB에서 유저 조회
            auth_entry = db.query(Auth).filter(Auth.refresh_token == refresh_token, Auth.access_token == access_token).first()

            if not auth_entry:
                logger.warning(f"expired refresh_token: {refresh_token}")
                return JSONResponse(status_code=200, content={"status": "expired_refresh_token", "detail": "Refresh token expired. Please log in again."})
            
            user_id = auth_entry.user_id

            # 새 엑세스 토큰 발급
            new_access_token = create_access_token(
                data={"user_id": user_id, "user_email": auth_entry.user.email},
                expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
            # UTC -> KST 변환 후 DB 업데이트
            access_created_at_utc = datetime.utcnow()
            access_created_at_kst = access_created_at_utc.astimezone(KST)
            access_expired_at_kst = access_created_at_kst + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
            auth_entry.access_token = new_access_token
            auth_entry.access_created_at = access_created_at_kst
            auth_entry.access_expired_at = access_expired_at_kst
            db.commit()
            
            logger.info(f"새로운 엑세스 토큰 발급 완료, 유저 ID: {user_id}")
            return JSONResponse(status_code=200, content={"status": "valid_refresh_token", "access_token": new_access_token, "detail": "Access token renewed."})
           
        except ExpiredSignatureError:
            logger.error("리프레시 토큰 만료됨.")
            return JSONResponse(status_code=200, content={"status": "expired_refresh_token", "detail": "Refresh token expired. Please log in again."})

        except JWTError:
            logger.error("유효하지 않은 리프레시 토큰.")
            return JSONResponse(status_code=200, content={"status": "expired_refresh_token", "detail": "Invalid refresh token."})
