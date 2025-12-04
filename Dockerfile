FROM python:3.11.9-slim

# Install Chrome and system dependencies for Selenium + OCR
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    gcc \
    g++ \
    libopenblas-dev \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port (Railway will set this dynamically)
EXPOSE 8000

# Run application - use shell form to allow environment variable expansion
CMD uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8000}
