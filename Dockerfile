FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/
COPY streamlit_app.py .

RUN mkdir -p /data /app/logs && chmod +x /app/scripts/start.sh

EXPOSE 8000
EXPOSE 8501

ENV LOG_FILE_PATH=/app/logs/app.log
ENV API_BASE_URL=http://127.0.0.1:8000

CMD ["/app/scripts/start.sh"]
