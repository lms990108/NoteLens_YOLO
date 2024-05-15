from yolov5 import test_detection

class YoloService:
    def __init__(self):
        self.yoloservice = test_detection
    
    def detect_objects(self, image_path):
        # 이미지에서 객체 탐지하고 크롭된 이미지들 yolov5/runs/detect/ 아래에 저장
        self.yoloservice(source=image_path)
        