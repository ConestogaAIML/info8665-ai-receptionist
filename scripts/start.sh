#!/bin/sh
set -e

mkdir -p /app/logs /data /app/data/model /app/data/processed /app/data/raw

cd /app
python scripts/docker_seed.py

# Ensure no-show model exists (train from processed/raw data if artifact missing)
if [ ! -f /app/data/model/no_show_model.pkl ]; then
  echo "No-show model missing — running preprocess + train..."
  python -c "from app.services.preprocess_data import preprocess_appointments; preprocess_appointments()"
  python -c "from app.services.train_model import train_no_show_model; print(train_no_show_model())"
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 &

node /app/frontend/server.js &

streamlit run streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true \
  --browser.gatherUsageStats false
