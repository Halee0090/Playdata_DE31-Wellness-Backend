# /app/main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.v1 import recommend, model, user, auth
from db import models
from api.v1.history import router as history_router
from core.logging import setup_logging
import logging
from starlette.exceptions import HTTPException as StarletteHTTPException
# 로깅 설정 초기화
logger = setup_logging()

# fastapi 앱 생성
app = FastAPI()

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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth_kakaotoken"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(recommend.router, prefix="/api/v1/recommend", tags=["Recommend"])
app.include_router(model.router, prefix="/api/v1/model", tags=["Model"]) 
app.include_router(history_router, prefix="/api/v1/history", tags=["History"])

# 서버 시작 시 로그 출력
logger.info("FastAPI application has started.")
  
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

