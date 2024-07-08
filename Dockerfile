
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
    && pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

