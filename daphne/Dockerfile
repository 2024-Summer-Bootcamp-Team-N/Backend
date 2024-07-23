FROM python:3.9-slim-bullseye

WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    chromium \
    chromium-driver \
    redis-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 사용자 및 그룹 생성
RUN groupadd -r myuser && useradd -r -g myuser myuser

# requirements.txt 파일 복사 및 종속성 설치
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install celery python-dotenv

# 애플리케이션 파일 복사
COPY .. .

# 권한 설정
RUN chown -R myuser:myuser /app

# Daphne 실행
CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "config.asgi:application"]
