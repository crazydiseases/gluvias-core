# === STAGE 1: BUILD THE NEXT.JS FRONTEND ===
FROM node:22-alpine AS frontend-builderWORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# Build the Next.js app as a static export
RUN npx next build

# === STAGE 2: BUILD THE FASTAPI BACKEND & SERVE ASSETS ===
FROM python:3.11-slim
WORKDIR /app

# Install system and python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY main.py .
COPY dashboard.html .
COPY index.html .

# Copy the compiled static assets from Stage 1 into a folder FastAPI can see
COPY --from=frontend-builder /app/frontend/out ./static_frontend

EXPOSE 8080
CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "8080"]
