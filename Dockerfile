FROM python:3.9

WORKDIR /app

COPY requirements.txt .

# Update package lists, install required packages and MySQL client
RUN apt-get update \
    && apt-get install -y \
       git \
       default-libmysqlclient-dev \
       build-essential \
       wget \
       unzip \
       xvfb \
       libxi6 \
       libgconf-2-4 \
       gnupg2 \
       curl \
       chromium \
       chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set permissions for chromedriver
RUN chmod +x /usr/bin/chromedriver

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 사용자 및 그룹 생성
RUN groupadd -r myuser && useradd -r -g myuser myuser

# 포트 노출
EXPOSE 8000

# 비루트 사용자로 실행
USER myuser

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]