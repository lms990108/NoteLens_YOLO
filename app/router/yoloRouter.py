from fastapi import APIRouter, File, UploadFile, HTTPException
import requests
from typing import List, Dict
import os
from io import BytesIO



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


# api 정의
# 이미지를 파일로 직접 받아서 YOLOv5로 객체 탐지 수행
@yoloRouter.post("/yolo", response_model=Dict[str, List[str]])
async def process_image(file: UploadFile = File(...), ):
    
    # 몽고아이디
    mongo_id = "test_mongo_id"
    
    # 임시 저장할 파일 경로
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    logger.info(f"임시 파일 경로: {temp_file_path}")
    
    # yolo로 이미지 크롭, ocr 수행 후 결과 리턴
    yolov5_service.textDetection(image_path=temp_file_path, mongo_id=mongo_id)
    logger.info("YOLOv5 /yolo FILE 객체 탐지를 성공적으로 수행했습니다.")
    
    # 임시 파일 삭제
    os.remove(temp_file_path)
    logger.info("임시 파일을 성공적으로 삭제했습니다 - 욜로 크롭 수행 종료")
    
    # 몽고아이디로 파일에 접근
    dir_path = Path("yolov5") / "runs" / "detect" / mongo_id / "crops" / "underline text"
    
    
    # url = "http://localhost:8000/api/ocr/ocr-multi" # 로컬 테스트용 주소
    # 크롭된 이미지들을 ocr 서비스로 전달
    url = "http://43.203.54.176:8000/api/ocr/ocr-multi" # ocr 서비스 주소
    files_data = []
    open_files = []  # 파일 객체들을 이후 close 하기 위한 리스트
    for file_path in dir_path.glob("*.jpg"):
        f = open(file_path, "rb")
        files_data.append(('files', (file_path.name, f, 'image/jpeg')))
        open_files.append(f)  # 나중에 닫기 위해 파일 객체 저장
    
    # logger.info("httpx 작업 전 - files_data: ", files_data)
    
    
    async with httpx.AsyncClient() as client:

        try:
            # logger.info("httpx 작업 중 - files_data: ", files_data)
            response = await client.post(url, files=files_data)
            
            logger.info("httpx 작업 중 - await 이후")
            response.raise_for_status()  # 응답 상태 코드가 4xx 또는 5xx인 경우 예외 발생
            
            logger.info("httpx 작업 수행됨 올바른지 아닌지 모름")
            try:
                result_texts = response.json()
                return result_texts
            except Exception as e:
                logger.error(f"Error while parsing response: {e}")
                raise HTTPException(status_code=500, detail="Error while parsing response")
        
        except httpx.RequestError as exc:
            # 요청 중에 발생한 네트워크 오류 처리
            raise HTTPException(status_code=500, detail=f"Error while requesting server2: {exc}")
        except httpx.HTTPStatusError as exc:
            # 서버2에서 반환한 오류 상태 코드 처리
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response from server2: {exc.response.text}")
        except Exception as exc:
            # 기타 예외 처리
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")
        finally:
            for f in open_files:
                f.close()  # 모든 파일 객체 닫기
            for file_path in dir_path.glob("*.jpg"):
                os.remove(file_path) # 크롭된 이미지 파일 삭제
            logger.info("모든 파일 객체를 닫았습니다.")



# url로 이미지를 받아서 YOLOv5로 객체 탐지 수행
# 아직 몽고아이디를 받아서 처리하는 부분은 없음
@yoloRouter.post("/yolo-from-url", response_model=List[str])
async def process_image_from_url(image_url: str):
    
    # 몽고아이디
    mongo_id = "test_mongo_id"
    
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # 에러가 발생하면 HTTPException을 발생시킵니다.
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

    image_bytes = BytesIO(response.content)
    temp_image_path = f"temp_{image_url.split('/')[-1]}"
    
    with open(temp_image_path, 'wb') as image_file:
        image_file.write(image_bytes.read())

    yolov5_service.textDetection(temp_image_path)
    
    os.remove(temp_image_path)
    
    dir_path = Path("yolov5") / "runs" / "detect" / mongo_id / "crops" / "underline text"
    
    # 멀티 파일 전송 테스트
    # url = "http://localhost:8000/api/ocr/ocr-multi" # 로컬 테스트용 주소
    # 크롭된 이미지들을 ocr 서비스로 전달
    url = "http://43.203.54.176:8000/api/ocr/ocr-multi" # ocr 서비스 주소
    files_data = []
    open_files = []  # 파일 객체들을 이후 close 하기 위한 리스트
    for file_path in dir_path.glob("*.jpg"):
        f = open(file_path, "rb")
        files_data.append(('files', (file_path.name, f, 'image/jpeg')))
        open_files.append(f)  # 나중에 닫기 위해 파일 객체 저장
    
    # logger.info("httpx 작업 전 - files_data: ", files_data)
    
    
    async with httpx.AsyncClient() as client:

        try:
            # logger.info("httpx 작업 중 - files_data: ", files_data)
            response = await client.post(url, files=files_data)
            
            logger.info("httpx 작업 중 - await 이후")
            response.raise_for_status()  # 응답 상태 코드가 4xx 또는 5xx인 경우 예외 발생
            
            logger.info("httpx 작업 수행됨 올바른지 아닌지 모름")
            try:
                result_texts = response.json()
                return result_texts
            except Exception as e:
                logger.error(f"Error while parsing response: {e}")
                raise HTTPException(status_code=500, detail="Error while parsing response")
        
        except httpx.RequestError as exc:
            # 요청 중에 발생한 네트워크 오류 처리
            raise HTTPException(status_code=500, detail=f"Error while requesting server2: {exc}")
        except httpx.HTTPStatusError as exc:
            # 서버2에서 반환한 오류 상태 코드 처리
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error response from server2: {exc.response.text}")
        except Exception as exc:
            # 기타 예외 처리
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")
        finally:
            for f in open_files:
                f.close()  # 모든 파일 객체 닫기
            logger.info("모든 파일 객체를 닫았습니다.")
