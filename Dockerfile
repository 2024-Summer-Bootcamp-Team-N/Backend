FROM python:3.9

WORKDIR /app

COPY requirements.txt .

# Update package lists, install git, and install MySQL client
RUN apt-get update \
    && apt-get install -y git default-libmysqlclient-dev build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install celery
# 사용자 및 그룹 생성
RUN groupadd -r myuser && useradd -r -g myuser myuser
# 포트 노출.
EXPOSE 8000

# 비루트 사용자로 실행
USER myuser

COPY . .

#웹서버 / 셀러리 시작 (우선은 로컬)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

