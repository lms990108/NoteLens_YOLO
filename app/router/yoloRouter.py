from fastapi import APIRouter, File, UploadFile, HTTPException
import requests
from typing import List
import os
from io import BytesIO

# from ..service.ocrService import OCRService
from ..service.yoloService import YoloService


# OCR 서비스 인스턴스화
yolo_service = YoloService()
yoloRouter = APIRouter()

@yoloRouter.post("/yolo", response_model=List[str])
async def process_image(file: UploadFile = File(...)):
    # yolo로 이미지 크롭 실행
    yolo_service.detect_objects(file)

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
    
    yolo_service.detect_objects(image_path)