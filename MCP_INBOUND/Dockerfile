# 베이스 이미지
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 생성
WORKDIR /app

# 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 컨텍스트 디렉토리 미리 생성
RUN mkdir -p context

# FastAPI 앱 실행
CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
