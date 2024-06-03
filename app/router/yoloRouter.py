from fastapi import APIRouter, File, UploadFile, HTTPException, status
import requests
from typing import List, Dict
import os
from io import BytesIO


import shutil
from pathlib import Path
import httpx
import logging
from app.service.yoloService import YOLOv5Service


# 로그 설정
logging.config.fileConfig('app/config/logging_config.ini')
logger = logging.getLogger(__name__)

# 윈도우에서만 실행할 코드 - PosixPath를 WindowsPath로 변경
if os.name == 'nt':
    from pathlib import Path
    import pathlib
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath
else:
# 리눅스 환경
    from pathlib import Path


# YOLOv5 서비스 인스턴스 생성 (사용자 지정 가중치 경로를 전달)
weights_path = 'yolov5/weights/best.pt'
yolov5_service = YOLOv5Service()
logger.info(f"YOLOv5 가중치 경로: {weights_path}")

yoloRouter = APIRouter()

# SERVER2_HEALTH_URL = "http://localhost:8000/api/test/health" # 로컬 테스트용 주소
# SERVER2_OCR_MULTI_URL = "http://localhost:8000/api/ocr/ocr-multi" # 로컬 테스트용 주소
# 서버2의 주소 및 OCR 서비스 주소
SERVER2_HEALTH_URL = "http://43.203.54.176:8000/api/test/health"
SERVER2_OCR_MULTI_URL = "http://43.203.54.176:8000/api/ocr/ocr-multi" # 이민섭 ocr서버 api 주소
# SERVER2_OCR_MULTI_URL = "http://43.203.93.209:8000/api/ocr/ocr-multi" # 주영운 ec2의 ocr서버 api 주소

# 통신하는 서버가 정상적으로 작동하는지 확인하는 함수
async def is_server2_healthy():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(SERVER2_HEALTH_URL, timeout=5)
            if response.status_code == status.HTTP_200_OK and response.json().get("status") == "ok":
                return True
        except httpx.RequestError:
            return False
    return False

# api 정의
# 이미지를 파일로 직접 받아서 YOLOv5로 객체 탐지 수행
@yoloRouter.post("/yolo", response_model=Dict[str, str])
async def process_image(file: UploadFile = File(...), ):
    
    # 서버2가 정상적으로 작동하는지 확인
    if not await is_server2_healthy():
        logger.error("Server2 is not healthy")
        raise HTTPException(status_code=500, detail="Server2 is not healthy")
    
    # 몽고아이디
    mongo_id = "test_mongo_id"
    
    # 임시 저장할 파일 경로
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    logger.info(f"임시 파일 경로: {temp_file_path}")
    
    # yolo로 이미지 크롭 수행
    yolov5_service.textDetection(image_path=temp_file_path, mongo_id=mongo_id)
    logger.info("YOLOv5 /yolo FILE 객체 탐지를 성공적으로 수행했습니다.")
    
    # 임시 파일 삭제
    os.remove(temp_file_path)
    logger.info("임시 파일을 성공적으로 삭제했습니다 - 욜로 크롭 수행 종료")
    
    # 몽고아이디로 파일에 접근
    dir_path = Path("yolov5") / "runs" / "detect" / mongo_id / "crops" / "underline text"
    remove_folder_path = Path("yolov5") / "runs" / "detect" / mongo_id
    
    files_data = []
    open_files = []  # 파일 객체들을 이후 close 하기 위한 리스트
    for file_path in dir_path.glob("*.jpg"):
        f = open(file_path, "rb")
        files_data.append(('files', (file_path.name, f, 'image/jpeg')))
        open_files.append(f)  # 나중에 닫기 위해 파일 객체 저장
    
    # 크롭된 파일들이 없을 경우 예외 처리
    if not files_data:
        # 모든 파일 객체 닫기
        for f in open_files:
            f.close()
        logger.info("모든 파일 객체를 닫았습니다.")
        # 폴더 및 하위 내용 삭제
        if os.path.exists(remove_folder_path):
            shutil.rmtree(remove_folder_path)
            logger.info(f"폴더 '{remove_folder_path}' 가 성공적으로 삭제되었습니다.")
        else:
            logger.info(f"폴더 '{remove_folder_path}' 가 존재하지 않습니다.")
        
        logger.error("크롭된 이미지 파일이 존재하지 않습니다.")
        raise HTTPException(status_code=404, detail="크롭된 이미지 파일이 존재하지 않습니다.")
    
    # 크롭된 이미지들을 ocr 서비스로 전달하는 코드
    logger.info(f"httpx 작업 전 - 수신지 url: {SERVER2_OCR_MULTI_URL}")
    async with httpx.AsyncClient() as client:

        try:
            # timeout_limit 만큼 기다리는 코드
            timeout_limit = 45
            response = await client.post(url=SERVER2_OCR_MULTI_URL, files=files_data, timeout=timeout_limit)
            response.raise_for_status()  # 응답 상태 코드가 4xx 또는 5xx인 경우 예외 발생
            
            result_texts = response.json()
            logger.info("httpx를 통해 ocr 서버의 api로부터 리턴값 받음")
            return result_texts
        
        except httpx.TimeoutException:
            # 요청 시간 초과 처리
            logger.error("Request timeout while requesting server2")
            raise HTTPException(status_code=504, detail=f"Server2 did not respond in time. timeout limit is {timeout_limit} seconds.")
        except httpx.RequestError as exc:
            # 요청 중에 발생한 네트워크 오류 처리
            logger.error(f"Request error while requesting server2: {exc}")
            raise HTTPException(status_code=500, detail=f"Error while requesting server2: {exc}")
        except httpx.HTTPStatusError as exc:
            # 서버2에서 반환한 오류 상태 코드 처리
            logger.error(f"HTTP error response from server2: {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response from server2: {exc.response.text}")
        except Exception as exc:
            # 기타 예외 처리
            logger.error(f"Unexpected error: {exc}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")
        finally:
            # 모든 파일 객체 닫기
            for f in open_files:
                f.close()  
            logger.info("모든 파일 객체를 닫았습니다.")
            
            # 폴더 및 그 내용 삭제
            if os.path.exists(remove_folder_path):
                shutil.rmtree(remove_folder_path)
                logger.info(f"폴더 '{remove_folder_path}' 가 성공적으로 삭제되었습니다.")
            else:
                logger.info(f"폴더 '{remove_folder_path}' 가 존재하지 않습니다.")



# url로 이미지를 받아서 YOLOv5로 객체 탐지 수행
# 아직 몽고아이디를 받아서 처리하는 부분은 없음
@yoloRouter.post("/yolo-from-url", response_model=Dict[str, str])
async def process_image_from_url(image_url: str):
    
    # 서버2가 정상적으로 작동하는지 확인
    if not await is_server2_healthy():
        logger.error("Server2 is not healthy")
        raise HTTPException(status_code=500, detail="Server2 is not healthy")
    
    # 몽고아이디
    mongo_id = "test_mongo_id"
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # 에러가 발생하면 HTTPException을 발생시킵니다.
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 이미지를 BytesIO 객체로 변환(이미지를 메모리에 잠시 저장함)
    image_bytes = BytesIO(response.content)
    
    # 임시 저장할 파일 경로
    temp_image_path = f"temp_{image_url.split('/')[-1]}"
    logger.info(f"임시 파일 경로: {temp_image_path}")
    
    with open(temp_image_path, 'wb') as image_file:
        image_file.write(image_bytes.read())
    
    # yolo로 이미지 크롭 수행
    yolov5_service.textDetection(image_path=temp_image_path, mongo_id=mongo_id)
    logger.info("YOLOv5 /yolo-from-url URL 객체 탐지를 성공적으로 수행했습니다.")
    
    # 임시 파일 삭제
    os.remove(temp_image_path)
    logger.info("임시 파일을 성공적으로 삭제했습니다 - 욜로 크롭 수행 종료")
    
    # 몽고아이디로 파일에 접근
    dir_path = Path("yolov5") / "runs" / "detect" / mongo_id / "crops" / "underline text"
    remove_folder_path = Path("yolov5") / "runs" / "detect" / mongo_id
    
    files_data = []
    open_files = []  # 파일 객체들을 이후 close 하기 위한 리스트
    for file_path in dir_path.glob("*.jpg"):
        f = open(file_path, "rb")
        files_data.append(('files', (file_path.name, f, 'image/jpeg')))
        open_files.append(f)  # 나중에 닫기 위해 파일 객체 저장
    
    # 크롭된 파일들이 없을 경우 예외 처리
    if not files_data:
        # 모든 파일 객체 닫기
        for f in open_files:
            f.close()
        logger.info("모든 파일 객체를 닫았습니다.")
        # 폴더 및 하위 내용 삭제
        if os.path.exists(remove_folder_path):
            shutil.rmtree(remove_folder_path)
            logger.info(f"폴더 '{remove_folder_path}' 가 성공적으로 삭제되었습니다.")
        else:
            logger.info(f"폴더 '{remove_folder_path}' 가 존재하지 않습니다.")
        
        logger.error("크롭된 이미지 파일이 존재하지 않습니다.")
        raise HTTPException(status_code=404, detail="크롭된 이미지 파일이 존재하지 않습니다.")
    
    # 크롭된 이미지들을 ocr 서비스로 전달하는 코드
    logger.info(f"httpx 작업 전 - 수신지 url: {SERVER2_OCR_MULTI_URL}")
    async with httpx.AsyncClient() as client:

        try:
            # timeout_limit 만큼 기다리는 코드
            timeout_limit = 45
            response = await client.post(url=SERVER2_OCR_MULTI_URL, files=files_data, timeout=timeout_limit)
            response.raise_for_status()  # 응답 상태 코드가 4xx 또는 5xx인 경우 예외 발생
            
            result_texts = response.json()
            logger.info("httpx를 통해 ocr 서버의 api로부터 리턴값 받음")
            return result_texts
        
        except httpx.TimeoutException:
            # 요청 시간 초과 처리
            logger.error("Request timeout while requesting server2")
            raise HTTPException(status_code=504, detail=f"Server2 did not respond in time. timeout limit is {timeout_limit} seconds.")
        except httpx.RequestError as exc:
            # 요청 중에 발생한 네트워크 오류 처리
            logger.error(f"Request error while requesting server2: {exc}")
            raise HTTPException(status_code=500, detail=f"Error while requesting server2: {exc}")
        except httpx.HTTPStatusError as exc:
            # 서버2에서 반환한 오류 상태 코드 처리
            logger.error(f"HTTP error response from server2: {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response from server2: {exc.response.text}")
        except Exception as exc:
            # 기타 예외 처리
            logger.error(f"Unexpected error: {exc}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")
        finally:
            # 모든 파일 객체 닫기
            for f in open_files:
                f.close()  
            logger.info("모든 파일 객체를 닫았습니다.")
            
            # 폴더 및 그 내용 삭제
            if os.path.exists(remove_folder_path):
                shutil.rmtree(remove_folder_path)
                logger.info(f"폴더 '{remove_folder_path}' 가 성공적으로 삭제되었습니다.")
            else:
                logger.info(f"폴더 '{remove_folder_path}' 가 존재하지 않습니다.")
