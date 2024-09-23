from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from pytz import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import APIRouter, Depends, Header, HTTPException
from db.models import Auth, User  # ORM 모델을 직접 사용
from db.session import get_db
from dotenv import load_dotenv
import os
from services.auth_service import create_access_token
from schemas.auth import TokenRequest  
from core.logging import logger
import pytz

# .env 파일 로드
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()

# 토큰 검증 및 재발급 API
@router.post("/verify")
async def verify_token(token_data: TokenRequest, authorization: str = Header(...), db: AsyncSession = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        logger.error("Invalid authorization format")
        raise HTTPException(status_code=400, detail="Invalid authorization format")

    access_token = authorization.split(" ")[1]
    refresh_token = token_data.refresh_token

    logger.info(f"Received Access Token for verification: {access_token}")
    logger.info(f"Received Refresh Token for verification: {refresh_token}")

    try:
        # 엑세스 토큰 검증
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        logger.info(f"엑세스 토큰 유효, 유저 ID: {user_id}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "VALID_ACCESS_TOKEN",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "detail": "Access token is still valid."
            }
        )

    except ExpiredSignatureError:
        logger.warning("엑세스 토큰 만료, 리프레시 토큰 확인 필요.")
        
        # 엑세스 토큰이 만료된 경우 리프레시 토큰으로 사용자 정보를 조회 (ORM 방식)
        stmt = select(Auth, User).join(User, Auth.user_id == User.id).where(Auth.refresh_token == refresh_token)
        result = await db.execute(stmt)
        auth_entry = result.first()

        if not auth_entry:
            logger.warning("Invalid Refresh Token.")
            return JSONResponse(
                status_code=401,
                content={
                    "status": "EXPIRED_REFRESH_TOKEN",
                    "access_token": None,
                    "refresh_token": None,
                    "detail": "Refresh token expired. Please log in again."
                }
            )

        # 사용자 정보 추출
        auth, user = auth_entry  # auth_entry는 Auth와 User 객체를 포함하는 튜플
        user_id = auth.user_id
        user_email = user.email
        logger.info(f"User ID: {user_id}, Email: {user_email}로 새로운 엑세스 토큰 발급")

        # 새 엑세스 토큰 발급
        new_access_token = create_access_token(
            data={"sub": user_id, "user_email": user_email},
            expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        # KST 타임존으로 시간 변환
        KST = pytz.timezone('Asia/Seoul')
        access_created_at_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)
        access_expired_at_utc = access_created_at_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_created_at_kst = access_created_at_utc.astimezone(KST)
        access_expired_at_kst = access_expired_at_utc.astimezone(KST)

        # DB에 새로운 엑세스 토큰 정보 업데이트 (ORM 방식)
        auth.access_token = new_access_token
        auth.access_created_at = access_created_at_kst
        auth.access_expired_at = access_expired_at_kst
        await db.commit()

        return JSONResponse(
            status_code=200,
            content={
                "status": "VALID_REFRESH_TOKEN",
                "access_token": new_access_token,
                "refresh_token": refresh_token,
                "detail": "Access token renewed."
            }
        )

    except JWTError as jwt_error:
        logger.error(f"Invalid Token. Error: {jwt_error}")
        return JSONResponse(
            status_code=401,
            content={
                "status": "INVALID_TOKEN",
                "access_token": None,
                "refresh_token": None,
                "detail": "Invalid token."
            }
        )
