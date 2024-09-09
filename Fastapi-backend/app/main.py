# /app/main.py
from fastapi import FastAPI
from app.api.v1 import recommend, model

app = FastAPI()

app.include_router(recommend.router, prefix="/recommend", tags=["Recommend"])
app.include_router(model.router, prefix="/model", tags=["Model"])

if __name__ == "__main__":
    import uvicorn
    uvicorn
