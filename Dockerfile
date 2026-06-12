FROM python:3.11-slim

WORKDIR /app

# Install basic OS system maintenance patches if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /lib/apt/lists/*

# Copy the dependency matrix first to leverage build caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our unified system engine file
COPY main.py .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
