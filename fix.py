import os
import shutil
import time

filepath = os.path.join(".github", "workflows", "deploy.yml")

print(f"Checking for broken directory at {filepath}...")

# 1. Check if the broken folder exists and delete it
if os.path.isdir(filepath):
    print("Found broken folder. Deleting it to make room for the file...")
    shutil.rmtree(filepath)
    time.sleep(1) # wait for filesystem to catch up

# 2. Write the actual YAML file
content = """version: '3.8'

services:
  backend:
    build: 
      context: ../../backend
      dockerfile_inline: |
        FROM python:3.12-slim
        ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FLASK_ENV=production
        WORKDIR /app
        RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY . .
        EXPOSE 5000
        CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:create_app()"]
    container_name: extension_backend
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - ../../backend/.env
    volumes:
      - ../../backend/data:/app/data
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: extension_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
"""

try:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Success! Correctly created the FILE: {filepath}")
    
    # Clean up the temp file if it exists
    alt_file = os.path.join(".github", "workflows", "docker_deploy.yml")
    if os.path.exists(alt_file):
        os.remove(alt_file)
        
except Exception as e:
    print(f"❌ Failed to write file: {e}")
