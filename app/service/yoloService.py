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
        # try:
        #     if weights_path:
        #         # 사용자 지정 가중치 파일을 사용하여 모델 로드
        #         # self.model = torch.hub.load('/yolov5', 'custom', path=weights_path)
        #         # 로컬 레포의 yolov5, 커스텀 가중치 파일로 모델 로드
        #         self.model = torch.hub.load('yolov5', 'custom', source='local', path=weights_path)
        #         logger.info(f"YOLOv5 모델이 {weights_path}에서 가중치를 성공적으로 로드했습니다.")
        #     else:
        #         # 기본 사전 학습된 yolov5s 모델 로드
        #         self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        #         logger.info("YOLOv5 사전 학습된 모델이 성공적으로 로드되었습니다.")
        # except Exception as e:
        #     logger.error(f"YOLOv5 모델 로드 중 오류 발생: {e}")
        #     raise
        
        self.test = test_detection.run
    
    def test_detect(self, image_path):
        logger.info("test_detect 함수 실행")
        # 객체 탐지 수행

        results = self.test(source=image_path)
        logger.info("test_detect 내 test_detection 함수를 성공적으로 수행했습니다.")
        
        # 탐지된 객체의 위치 정보를 사용하여 이미지를 잘라냅니다.
        cropped_images = []
        for result in results:
            # 객체의 좌표를 가져와서 이미지를 잘라냅니다.
            x1, y1, x2, y2 = result['bbox']
            cropped_img = image_path.crop((x1, y1, x2, y2))
            cropped_images.append(cropped_img)

        logger.info("크롭 이미지 리턴")
        return cropped_images
        

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