#!/bin/bash
# Entrypoint script to run both backend and frontend

# Start backend (FastAPI/Uvicorn)
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start frontend (Streamlit)
cd /app/frontend && streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
