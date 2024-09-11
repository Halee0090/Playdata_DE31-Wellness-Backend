# /app/main.py
from fastapi import FastAPI
from api.v1 import recommend, model, user
from db import models
from api.v1.history import router as history_router

app = FastAPI()

app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(recommend.router, prefix="/api/v1/recommend", tags=["Recommend"])
app.include_router(model.router, prefix="/api/v1/model", tags=["Model"]) 
app.include_router(history_router, prefix="/api/v1/history", tags=["History"])
  
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

