# ---- Frontend build stage ----
FROM node:22-slim AS frontend-builder
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# ---- Final image: backend + frontend ----
FROM python:3.11-slim

# Node.js runtime to serve the pre-built Next.js standalone app
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY dev/ ./dev/
COPY scripts/ ./scripts/
COPY training/ ./training/
COPY data-collection/ ./data-collection/
COPY ml-assets/ ./ml-assets/
COPY streamlit_app.py .
COPY .env.example ./.env.example

COPY --from=frontend-builder /frontend/public ./frontend/public
COPY --from=frontend-builder /frontend/.next/standalone ./frontend/
COPY --from=frontend-builder /frontend/.next/static ./frontend/.next/static

# Seed ML paths from tracked assets (data/ is gitignored; CI-safe)
RUN mkdir -p /data /app/logs /app/data/model /app/data/processed /app/data/raw \
    && cp /app/ml-assets/appointments.csv /app/data/raw/appointments.csv \
    && cp /app/ml-assets/processed_appointments.csv /app/data/processed/processed_appointments.csv \
    && chmod +x /app/scripts/start.sh \
    && ML_EPOCHS=1 ML_N_ESTIMATORS=50 \
       python -c "from app.services.train_model import train_no_show_model; print(train_no_show_model())"

EXPOSE 8000
EXPOSE 8501
EXPOSE 3000

ENV LOG_FILE_PATH=/app/logs/app.log
ENV API_BASE_URL=http://127.0.0.1:8000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
ENV DB_ENGINE=sqlite
ENV SQLITE_DB_PATH=/data/receptionist.db
ENV MODEL_PATH=data/model/no_show_model.pkl
ENV PROCESSED_DATA_PATH=data/processed/processed_appointments.csv

CMD ["/app/scripts/start.sh"]
