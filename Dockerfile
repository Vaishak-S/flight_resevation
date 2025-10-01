# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./
COPY backend/requirements.txt ./backend/requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r backend/requirements.txt \
    && pip install streamlit uvicorn fastapi

# Copy project files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# Expose ports for backend and frontend
EXPOSE 8000 8501

# Start both backend and frontend
CMD ["./entrypoint.sh"]
