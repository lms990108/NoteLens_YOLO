import torch
import logging
from PIL import Image
import io


from yolov5 import detection
from torchvision.transforms import functional as F


logging.config.fileConfig('app/config/logging_config.ini')
logger = logging.getLogger(__name__)

logger.info("YOLOv5Service 클래스 정의")

class YOLOv5Service:
    def __init__(self):
        self.detection = detection.run
    
    def textDetection(self, image_path, mongo_id):
        
        logger.info("test_detect 함수 실행")
        # 크롭된 이미지들이 경로에 저장됨
        self.detection(source=image_path, mongo_id=mongo_id)
