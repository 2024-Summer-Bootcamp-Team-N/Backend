FROM python:3.9-slim-bullseye

WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    supervisor \
    chromium \
    chromium-driver \
    redis-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 사용자 및 그룹 생성
RUN groupadd -r myuser && useradd -r -g myuser myuser

# requirements.txt 파일 복사 및 종속성 설치
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install celery python-dotenv

# 애플리케이션 파일 복사
COPY . .

# 권한 설정
RUN mkdir -p /var/log && touch /var/log/django.log /var/log/daphne.log /var/log/django.err /var/log/daphne.err && \
    chown -R myuser:myuser /app /var/log/django.log /var/log/daphne.log /var/log/django.err /var/log/daphne.err

# Supervisord 설정 파일 복사
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Supervisord 실행
CMD ["supervisord", "-c", "/app/supervisord.conf"]