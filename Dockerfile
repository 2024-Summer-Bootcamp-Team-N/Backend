# 사용할 Python 이미지
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 포트 8000 열기
EXPOSE 8000

# 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
