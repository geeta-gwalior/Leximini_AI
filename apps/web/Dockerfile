FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/web ./apps/web

EXPOSE 8501

CMD ["streamlit", "run", "apps/web/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
