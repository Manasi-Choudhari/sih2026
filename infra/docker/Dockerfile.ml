FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ML_DEVICE=cpu

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY ml/requirements.txt /app/ml/requirements.txt
RUN pip install --no-cache-dir -r /app/ml/requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn

COPY ml /app/ml

EXPOSE 8001

# Day 1 stub: T3 will replace this with their ML service entry point (e.g. FastAPI app)
# For now, keeps container alive so docker compose up succeeds for all teammates
CMD ["python", "-c", "import time; print('VAJRA ML Service ready (stub — awaiting T3 entry point).'); time.sleep(360000)"]
