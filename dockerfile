# 베이스 이미지를 yolov5 최신 cpu 버전의 공식 이미지로 지정
FROM ultralytics/yolov5:latest-cpu

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 Python 패키지 설치
RUN pip install fastapi "uvicorn[standard]"

# 현재 디렉토리의 모든 파일을 컨테이너의 /app으로 복사
COPY . /app

# 스크립트 파일에 실행 권한 부여
RUN chmod +x run_prod_server.sh

# 외부로 노출할 포트 지정
EXPOSE 8001

# 컨테이너 실행 시 기본 명령 지정
CMD ["/bin/bash", "./run_prod_server.sh"]