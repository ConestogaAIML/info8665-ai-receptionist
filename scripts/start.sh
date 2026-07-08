#!/bin/sh
set -e

mkdir -p /app/logs /data

uvicorn app.main:app --host 0.0.0.0 --port 8000 &

streamlit run streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false

