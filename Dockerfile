FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY configs/ ./configs/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY bmo-etf-firebase-adminsdk-fbsvc-d7943182ab.json ./

EXPOSE ${PORT:-8000}

CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

