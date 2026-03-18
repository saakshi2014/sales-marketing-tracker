# Use official Python slim image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 5000
EXPOSE 5000

# Run Flask
CMD ["python", "backend/app.py"]