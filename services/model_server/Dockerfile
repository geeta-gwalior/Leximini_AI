FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/model_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/model_server ./services/model_server

EXPOSE 8002

CMD ["uvicorn", "services.model_server.main:app", "--host", "0.0.0.0", "--port", "8002"]
