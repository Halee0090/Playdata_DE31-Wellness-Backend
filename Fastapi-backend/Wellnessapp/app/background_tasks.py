import asyncio
from datetime import datetime, timedelta
import pytz
import boto3
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from db import crud
from db.crud import get_daily_logs, delete_old_logs
from db.session import async_session

async def generate_daily_log():
    s3 = boto3.client('s3')
    bucket_name = 'finalteambucket'

    while True:
        korea_timezone = pytz.timezone('Asia/Seoul')
        now = datetime.now(korea_timezone)
        yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        # 한국 시간을 UTC로 변환
        yesterday_utc = yesterday.astimezone(pytz.utc)

        async with async_session() as session:
            logs = await crud.get_daily_logs(session, yesterday_utc)

            filename = f"{yesterday.strftime('%Y-%m-%d')}-errors.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                for log in logs:
                    # 로그의 타임스탬프를 한국 시간으로 변환
                    log_time_korea = log.time_stamp.astimezone(korea_timezone)
                    f.write(f"{log_time_korea}: {log.method} {log.req_url} - {log.code}\n")

            # S3 업로드 (필요 시 주석 해제)
            # s3.upload_file(filename, bucket_name, f"logs/{filename}")

            await crud.delete_old_logs(session, 30)

        # 다음 날 대기
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        await asyncio.sleep((tomorrow - now).total_seconds())