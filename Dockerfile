FROM python:3.9-slim

# install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# create directory for credentials
RUN mkdir -p /app/credentials

# set environment variables
ENV PYTHONPATH=/app
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-credentials.json

# expose port
EXPOSE 8080

# run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]