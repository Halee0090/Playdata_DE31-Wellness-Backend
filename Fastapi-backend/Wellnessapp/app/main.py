# /app/main.py
from fastapi import FastAPI
from Wellnessapp.app.api.v1 import recommend, model, user
from Wellnessapp.app.db import models
from pytz import timezone
from Wellnessapp.app.api.v1.history import router as history_router

app = FastAPI()

app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(recommend.router, prefix="/api/v1/recommend", tags=["Recommend"])
app.include_router(model.router, prefix="/api/v1/model", tags=["Model"]) 
app.include_router(history_router, prefix="/api/v1/history")
  
if __name__ == "__main__":
    import uvicorn
    uvicorn

