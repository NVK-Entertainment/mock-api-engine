# Python version
FROM python:3.13-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Base project directory
WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Project code
COPY src ./src

# Startup directory
WORKDIR /app/src

# Port
EXPOSE 8000

# Startup command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]