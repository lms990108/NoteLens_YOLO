import torch
import logging
from PIL import Image
import io


from yolov5 import test_detection
from torchvision.transforms import functional as F


logging.config.fileConfig('app/config/logging_config.ini')
logger = logging.getLogger(__name__)

logger.info("YOLOv5Service 클래스 정의")

class YOLOv5Service:
    def __init__(self):
        self.detection = test_detection.run
    
    def textDetection(self, image_path, mongo_id):
        
        logger.info("test_detect 함수 실행")
        # 크롭된 이미지들이 경로에 저장됨
        self.detection(source=image_path, mongo_id=mongo_id)
        




    # mongo_id로 접근하는 것이 최종 목표
    # def textDetectionAndOCR(self, image_path, mongo_id): 
        # logger.info("test_detect 함수 실행")
        
        # # 크롭된 이미지들이 경로에 저장됨
        # self.test(source=image_path, mongo_id=mongo_id)
        # logger.info("test_detect 내 test_detection 함수를 성공적으로 수행했습니다.")
        
        # # 크롭된 이미지들을 ocr 서비스로 전달
        
        
        # # ocr 서비스로부터 결과를 받아서 리턴
        
        
        
        # logger.info("이미지의 텍스트 탐지 및 OCR의 결과 리턴")
        # return result_texts
