# /app/main.py
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import OAuth2PasswordBearer
from requests import session
from api.v1 import recommend, model, register, oauth, login
from api.v1.auth import validate_token
from db import models
from db.session import get_db
from db.models import Auth
from api.v1.history import router as history_router
import logging
import os
import time
from db.crud import create_log, get_daily_logs, delete_old_logs
from schemas.log import LogCreate
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import engine
from db.session import AsyncSessionLocal, get_db
import pytz
import asyncio
import boto3 
# S3 설정
S3_BUCKET = os.getenv('S3_BUCKET', 'finalteambucket')
s3_client = boto3.client('s3')

KST = pytz.timezone('Asia/Seoul')

# 로그 설정
log_file_path = os.path.join(os.getcwd(), "app.log")

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# fastapi 앱 생성
app = FastAPI()

# 일일 로그 파일 생성 및 S3 업로드
async def generate_daily_log():
    while True:
        now = datetime.utcnow()
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        await asyncio.sleep((next_day - now).total_seconds())
        
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT * FROM logs WHERE time_stamp >= :date", {"date": now.date()})
            logs = result.fetchall()
            
            log_file = fr"C:\Users\Playdata\backend\Fastapi-backend\Wellnessapp\app\daily_logs_txt\{now.strftime('%Y-%m-%d')}-errors.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                for log in logs:
                    f.write(f"{log.time_stamp}: {log.method} {log.req_url} - {log.code}\n")
            
            # # S3에 업로드 >>>허용 확인해야함
            # s3_client.upload_file(log_file, S3_BUCKET, f"logs/{log_file}")
            # os.remove(log_file)
            
            # 30일 이상 된 로그 삭제
            thirty_days_ago = now - timedelta(days=30)
            await session.execute("DELETE FROM logs WHERE time_stamp < :date", {"date": thirty_days_ago})
            await session.commit()

# 앱 시작 시 일일 로그 생성 태스크 시작
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generate_daily_log())


# 요청 및 응답을 기록하는 미들웨어 추가
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 요청 정보 기록
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    # 요청 파라미터 캡처
    req_param = str(request.query_params)
    
    # 요청 처리 시간 측정
    start_time = time.time()
    
    # 요청을 처리하여 응답 생성
    response = await call_next(request)

    # 응답 바디 캡처
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    # 처리 완료 후, 응답 시간 기록
    duration = time.time() - start_time
    logger.info(f"Completed request in {duration:.2f}s - Status Code: {response.status_code}")
    
    # 로그 엔트리 생성
    log_entry = LogCreate(
        req_url=str(request.url),
        method=request.method,
        req_param=req_param,
        res_param=response_body.decode(),
        msg="Request completed",
        code=response.status_code,
        time_stamp=datetime.now(KST)
    )

    async with AsyncSession(engine) as db:
        await create_log(db, log_entry)

    return Response(content=response_body, status_code=response.status_code, 
                    headers=dict(response.headers), media_type=response.media_type)
    

# 전역 예외 처리: HTTP 예외 처리
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP Exception: {exc.detail} - Request URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# 전역 예외 처리: 유효성 검사 처리
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error: {exc.errors()} - Request URL: {request.url}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )

# api 라우터 설정
# app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["Oauth_kakaotoken"])
app.include_router(login.router, prefix="/api/v1/user", tags=["user_Login"])
app.include_router(register.router, prefix="/api/v1/user", tags=["user_Register"])
app.include_router(recommend.router, prefix="/api/v1/recommend", tags=["Recommend"], dependencies=[Depends(validate_token)])
app.include_router(model.router, prefix="/api/v1/model", tags=["Model"], dependencies=[Depends(validate_token)])
app.include_router(history_router, prefix="/api/v1/history", tags=["History"], dependencies=[Depends(validate_token)])
app.include_router(meal_records.router, prefix="/api/v1", tags=["meal_records"])

# 서버 시작 시 로그 출력
logger.info("FastAPI application has started.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
