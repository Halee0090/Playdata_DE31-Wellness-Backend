# import asyncio
# from datetime import datetime, timedelta
# from fastapi import FastAPI, Request, Response
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import Column, Integer, String, Text, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# import json
# import boto3
# import os

# # FastAPI 앱 초기화
# app = FastAPI()

# # 데이터베이스 설정
# DATABASE_URL = os.getenv('DATABASE_URL', "postgresql+asyncpg://user:password@localhost/dbname?timezone=Asia/Seoul")
# engine = create_async_engine(DATABASE_URL, echo=True)
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# # S3 설정
# S3_BUCKET = os.getenv('S3_BUCKET', 'your-bucket-name')
# s3_client = boto3.client('s3')

# # SQLAlchemy 모델 정의
# Base = declarative_base()

# class Log(Base):
#     __tablename__ = 'logs'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     req_url = Column(String, nullable=False)
#     method = Column(String, nullable=False)
#     req_param = Column(Text, nullable=True)
#     res_param = Column(Text, nullable=True)
#     msg = Column(Text, nullable=False)
#     code = Column(Integer, nullable=False)
#     time_stamp = Column(DateTime, nullable=False)

# # 비동기 컨텍스트 매니저
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# # 로그 저장 함수
# async def log_request(request: Request, response: Response, msg: str):
#     async with AsyncSessionLocal() as session:
#         log = Log(
#             req_url=str(request.url),
#             method=request.method,
#             req_param=json.dumps(dict(request.query_params)),
#             res_param=response.body.decode(),
#             msg=msg,
#             code=response.status_code,
#             time_stamp=datetime.utcnow()
#         )
#         session.add(log)
#         await session.commit()

# # 미들웨어: 모든 요청 로깅
# @app.middleware("http")
# async def logging_middleware(request: Request, call_next):
#     response = await call_next(request)
#     await log_request(request, response, "Request logged")
#     return response

# # 일일 로그 파일 생성 및 S3 업로드
# async def generate_daily_log():
#     while True:
#         now = datetime.utcnow()
#         next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
#         await asyncio.sleep((next_day - now).total_seconds())
        
#         async with AsyncSessionLocal() as session:
#             result = await session.execute(f"SELECT * FROM logs WHERE time_stamp >= '{now.date()}'")
#             logs = result.fetchall()
            
#             log_file = f"{now.strftime('%Y-%m-%d')}-errors.txt"
#             with open(log_file, 'w') as f:
#                 for log in logs:
#                     f.write(f"{log.time_stamp}: {log.method} {log.req_url} - {log.code}\n")
            
#             # S3에 업로드
#             s3_client.upload_file(log_file, S3_BUCKET, f"logs/{log_file}")
#             os.remove(log_file)
            
#             # 30일 이상 된 로그 삭제
#             thirty_days_ago = now - timedelta(days=30)
#             await session.execute(f"DELETE FROM logs WHERE time_stamp < '{thirty_days_ago}'")
#             await session.commit()

# # 앱 시작 시 일일 로그 생성 태스크 시작
# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(generate_daily_log())

# # 여기에 FastAPI 라우트 추가
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# # 앱 실행 (uvicorn main:app --reload)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)