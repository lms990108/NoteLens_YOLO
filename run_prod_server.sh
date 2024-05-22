#!/bin/bash
set -x  # 명령어 실행을 로깅하여 보여줍니다.

# 시작 로그
echo "Starting script execution."

# uvicorn 실행
echo "** uvicorn 서버 실행 시작 **"
uvicorn main:app --host 0.0.0.0 --port 8001
echo "** uvicorn 서버 실행 종료 **"

echo "Script execution completed successfully."
