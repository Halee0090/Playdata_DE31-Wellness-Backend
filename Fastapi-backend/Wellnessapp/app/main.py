import asyncio
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import OAuth2PasswordBearer
from api.v1 import recommend, model, register, oauth, login
from api.v1.auth import validate_token
from db import models
from db.session import get_async_db
from db.models import Auth
from api.v1.history import router as history_router
import logging
import os
import time
from datetime import datetime
import pytz
from db import crud
from schemas import log as log_schema

os.environ['TZ'] = 'Asia/Seoul'

# 로그 설정
log_file_path = os.path.join(os.getcwd(), "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI 앱 생성
app = FastAPI()

# 한국시간 변환 함수
def utc_to_kst(utc_dt):
    kst_tz = pytz.timezone('Asia/Seoul')
    return utc_dt.astimezone(kst_tz)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 요청 본문 읽기
    body = await request.body()
    
    # 응답 처리
    response: Response = await call_next(request)
    
    # 응답 본문이 스트리밍일 경우 처리
    response_body = b""
    if hasattr(response, 'body'):
        response_body = await response.body()
    else:
        response_body = b""

    duration = time.time() - start_time

    # 현재 시간 UTC로 가져오기
    time_stamp_utc = datetime.utcnow()  # UTC로 설정
    # 한국 시간으로 변환
    time_stamp_kst = utc_to_kst(time_stamp_utc)

    # 로그 데이터 생성
    log_data = log_schema.LogCreate(
        req_url=str(request.url),
        method=request.method,
        req_param=body.decode() if body else str(request.query_params),
        res_param=response_body.decode(),
        msg=f"Request completed in {duration:.2f}s",
        code=response.status_code,
        time_stamp=time_stamp_kst  # 한국 시간으로 설정
    )
    
    async for db in get_async_db():
        await crud.create_log(db, log_data)
    
    # 원래의 응답을 반환
    return response

# PostgreSQL에서 KST로 변환된 로그 확인하는 쿼리
def get_logs_in_kst(db):
    return db.execute(
        "SELECT id, time_stamp AT TIME ZONE 'Asia/Seoul' AS time_stamp_kst FROM logs"
    ).fetchall()

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
app.include_router(login.router, prefix="/api/v1/user", tags=["user_Login"])
app.include_router(register.router, prefix="/api/v1/user", tags=["user_Register"])
app.include_router(recommend.router, prefix="/api/v1/recommend", tags=["Recommend"], dependencies=[Depends(validate_token)])
app.include_router(model.router, prefix="/api/v1/model", tags=["Model"], dependencies=[Depends(validate_token)])
app.include_router(history_router, prefix="/api/v1/history", tags=["History"], dependencies=[Depends(validate_token)])

# 백그라운드 태스크 추가
from background_tasks import generate_daily_log

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(generate_daily_log())

# 서버 시작 시 로그 출력
logger.info("FastAPI application has started.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
