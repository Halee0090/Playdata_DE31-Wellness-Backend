# /app/main.py
from fastapi import FastAPI
from app.api.v1 import recommend, model, user
from app.db import models
app = FastAPI()

app.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])
app.include_router(model.router, prefix="/model", tags=["Model"])
app.include_router(user.router, prefix="/user", tags=["User"])
if __name__ == "__main__":
    import uvicorn
    uvicorn
