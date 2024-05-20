from fastapi import APIRouter, File, UploadFile, HTTPException
import requests
from typing import List
import os
from io import BytesIO



from pathlib import Path
import httpx
import logging
from app.service.yoloService import YOLOv5Service

import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

# 로그 설정
logging.config.fileConfig('app/config/logging_config.ini')
logger = logging.getLogger(__name__)

# YOLOv5 서비스 인스턴스 생성 (사용자 지정 가중치 경로를 전달)
weights_path = 'yolov5/weights/best.pt'
yolov5_service = YOLOv5Service()
logger.info(f"YOLOv5 가중치 경로: {weights_path}")

yoloRouter = APIRouter()


# api 정의
# 이미지를 파일로 직접 받아서 YOLOv5로 객체 탐지 수행
@yoloRouter.post("/yolo", response_model=List[str])
async def process_image(file: UploadFile = File(...)):
    # 임시 저장할 파일 경로
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    logger.info(f"임시 파일 경로: {temp_file_path}")
    
    # yolo로 이미지 크롭, ocr 수행 후 결과 리턴
    # yolov5_service.test_textDetectionAndOCR(temp_file_path)
    logger.info("YOLOv5 /yolo FILE 객체 탐지를 성공적으로 수행했습니다.")
    
    # 임시 파일 삭제
    os.remove(temp_file_path)
    logger.info("임시 파일을 성공적으로 삭제했습니다.")
    
    # 몽고아이디로 파일에 접근
    mongo_id = "TEST_mongo_id"
    dir_path = Path("yolov5") / "runs" / "detect" / mongo_id / "crops" / "underline text"
    
    # 크롭된 이미지들을 files로 저장 TODO 구현 필요
    
    
    
    # 크롭된 이미지의 경로 설정
    file_path = dir_path / f"{mongo_id}.jpg"
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"File not found: {dir_path / '{mongo_id}.jpg'}")
    

    # 크롭된 이미지들을 ocr 서비스로 전달
    url = "http://43.203.54.176:8000/api/ocr/ocr" # ocr 서비스 주소
    async with httpx.AsyncClient() as client:

        try:
            with open(file_path, "rb") as f:
                files_data = {
                    'file': (Path(file_path).name, f, 'image/jpeg')
                }
                logger.info("httpx 작업 중 - files_data: ", files_data)
                response = await client.post(url, files=files_data)
            
            logger.info("httpx 작업 중 - await 이후")
            response.raise_for_status()  # 응답 상태 코드가 4xx 또는 5xx인 경우 예외 발생
            result_texts = response.json()
            logger.info("httpx 작업 수행됨 올바른지 아닌지 모름")
            return result_texts
        except httpx.RequestError as exc:
            # 요청 중에 발생한 네트워크 오류 처리
            raise HTTPException(status_code=500, detail=f"Error while requesting server2: {exc}")
        except httpx.HTTPStatusError as exc:
            # 서버2에서 반환한 오류 상태 코드 처리
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response from server2: {exc.response.text}")
        except Exception as exc:
            # 기타 예외 처리
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


# url로 이미지를 받아서 YOLOv5로 객체 탐지 수행
@yoloRouter.post("/yolo-from-url", response_model=List[str])
async def process_image_from_url(image_url: str):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # 에러가 발생하면 HTTPException을 발생시킵니다.
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    image_bytes = BytesIO(response.content)
    temp_image_path = f"temp_{image_url.split('/')[-1]}"
    
    with open(temp_image_path, 'wb') as image_file:
        image_file.write(image_bytes.read())

    result_texts = yolov5_service.test_textDetectionAndOCR(temp_image_path)
    
    os.remove(temp_image_path)
    
    # return result_texts
    