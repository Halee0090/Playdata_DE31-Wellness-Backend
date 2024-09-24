# /app/middlewares.py
from fastapi import Request
from core.logging import logger
import time

async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Completed request in {duration:.2f}s - Status Code: {response.status_code}")
    return response
