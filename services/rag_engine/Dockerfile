FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/rag_engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/rag_engine ./services/rag_engine
COPY data ./data

EXPOSE 8001

CMD ["uvicorn", "services.rag_engine.main:app", "--host", "0.0.0.0", "--port", "8001"]
