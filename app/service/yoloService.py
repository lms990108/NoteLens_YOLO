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
        self.test = test_detection.run
    
    def test_textDetectionAndOCR(self, image_path):
        logger.info("test_detect 함수 실행")
        
        # 크롭된 이미지들이 경로에 저장됨
        self.test(source=image_path)
        logger.info("test_detect 내 test_detection 함수를 성공적으로 수행했습니다.")
        
        
        
        
        # ocr 서비스로부터 결과를 받아서 리턴
        
        
        
        # logger.info("이미지의 텍스트 탐지 및 OCR의 결과 리턴")
        # return result_texts



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
    
    

    def detect_objects(self, image_path):
        
        logger.info("detect_objects 함수 실행")
        # 객체 탐지 수행

        results = test_detection(source=image_path)
        logger.info("detect_objects 내 test_detection 함수를 성공적으로 수행했습니다.")
        
        # 탐지된 객체의 위치 정보를 사용하여 이미지를 잘라냅니다.
        cropped_images = []
        for result in results:
            # 객체의 좌표를 가져와서 이미지를 잘라냅니다.
            x1, y1, x2, y2 = result['bbox']
            cropped_img = image_path.crop((x1, y1, x2, y2))
            cropped_images.append(cropped_img)

        logger.info("크롭 이미지 리턴")
        return cropped_images

        
        # try:
        #     # 객체 탐지 수행
        #     results = self.model(image_path)
        #     logger.info("객체 탐지를 성공적으로 수행했습니다.")
            
        #     results.print()
        #     results.save()

        #     results.xyxy[0]
        #     results.pandas().xyxy[0]

        #     return results
        # except Exception as e:
        #     logger.error(f"객체 탐지 중 오류 발생: {e}")
        #     raise