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
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 사용자 및 그룹 생성
RUN groupadd -r myuser && useradd -r -g myuser myuser

# requirements.txt 파일 복사 및 종속성 설치
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install celery python-dotenv gunicorn uvicorn

# 애플리케이션 파일 복사
COPY . .

# 권한 설정
RUN chown -R myuser:myuser /app

# 개발환경 / 배포환경으로 나눔
ENV DJANGO_SETTINGS_MODULE=config.settings
CMD if [ "$DJANGO_ENV" = "production2" ]; then daphne -b 0.0.0.0 -e ssl:8001:privateKey=/etc/letsencrypt/live/houseadvisor.site/privkey.pem:certKey=/etc/letsencrypt/live/houseadvisor.site/fullchain.pem config.asgi:application; else python manage.py runserver 0.0.0.0:8001; fi


# 사용자 권한으로 실행
USER myuser
