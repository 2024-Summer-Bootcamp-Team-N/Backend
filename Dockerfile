FROM python:3.9

WORKDIR /app

COPY requirements.txt .

# Add the necessary sources manually
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list

# Update package lists and install required packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
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
       chromium-driver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set permissions for chromedriver
RUN chmod +x /usr/bin/chromedriver

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create user and group
RUN groupadd -r myuser && useradd -r -g myuser myuser

# Expose port
EXPOSE 8000

# Switch to non-root user
USER myuser

COPY . .

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
