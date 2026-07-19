FROM python:3.11-slim

# poppler-utils zaroori hai pdf2image ke liye (system-level dependency, pip se nahi aata)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render $PORT env var provide karta hai runtime pe — hardcode mat karo
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]