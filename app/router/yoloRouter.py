from fastapi import APIRouter, File, UploadFile, HTTPException
import requests
from typing import List
import os
from io import BytesIO

import logging
from app.service.yoloService import YOLOv5Service




logging.config.fileConfig('app/config/logging_config.ini')
logger = logging.getLogger(__name__)

# YOLOv5 서비스 인스턴스 생성 (사용자 지정 가중치 경로를 전달)
weights_path = 'yolov5/weights/best.pt'
yolov5_service = YOLOv5Service()
logger.info(f"YOLOv5 가중치 경로: {weights_path}")


yoloRouter = APIRouter()

@yoloRouter.post("/yolo", response_model=List[str])
async def process_image(file: UploadFile = File(...)):
    # 임시 저장할 파일 경로
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    logger.info(f"임시 파일 경로: {temp_file_path}")
    
    # yolo로 이미지 크롭 실행
    rst = yolov5_service.test_detect(temp_file_path)
    logger.info("YOLOv5 /yolo FILE 객체 탐지를 성공적으로 수행했습니다.")
    
    # 임시 파일 삭제
    # os.remove(temp_file_path)
    # logger.info("임시 파일을 성공적으로 삭제했습니다.")
    
    return rst

    


@yoloRouter.post("/yolo-from-url", response_model=List[str])
async def process_image_from_url(image_url: str):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # 에러가 발생하면 HTTPException을 발생시킵니다.
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    # image_bytes = BytesIO(response.content)
    image_path = f"temp_{image_url.split('/')[-1]}"
    
    # with open(image_path, 'wb') as image_file:
    #     image_file.write(image_bytes.read())

    # texts = ocr_service.perform_ocr(image_path)
    
    # os.remove(image_path)
    
    # return texts
    
    yolov5_service.detect_objects(image_path)