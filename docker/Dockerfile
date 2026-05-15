# ── Base image ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ── Set working directory ──────────────────────────────────────────────────────
WORKDIR /app

# ── Install system dependencies ────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Copy requirements first (Docker layer caching) ─────────────────────────────
COPY backend/requirements.txt ./backend/requirements.txt

# ── Install Python packages ────────────────────────────────────────────────────
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Copy full project ──────────────────────────────────────────────────────────
COPY . .

# ── Set environment variables ──────────────────────────────────────────────────
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/backend

# ── Expose port ────────────────────────────────────────────────────────────────
EXPOSE 5000

# ── Run Flask ──────────────────────────────────────────────────────────────────
CMD ["python", "backend/app.py"]