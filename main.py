# 실행 명령어 uvicorn main:app --reload --port=8001
# 포트번호 : 8000번
# api list : localhost:8000/docs
from fastapi import FastAPI
from app.router import testRouter

app = FastAPI()

app.include_router(testRouter, prefix="/api/test")


