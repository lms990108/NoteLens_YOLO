# 실행 명령어 uvicorn main:app --reload --port=8001
# 포트번호 : 8000번
# api list : localhost:8001/docs
from fastapi import FastAPI
from app.router import imageRouter, yoloRouter

app = FastAPI()

app.include_router(imageRouter, prefix="/api/image")
app.include_router(yoloRouter, prefix="/api/yolo")