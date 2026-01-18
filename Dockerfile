# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies from PyPI
# omniagentpay should be available on PyPI, so install it normally
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy startup scripts
COPY start.sh /app/start.sh
COPY start.py /app/start.py
RUN chmod +x /app/start.sh /app/start.py

# Expose port (Cloud Run will set PORT env var)
EXPOSE 8080

# Use Python startup script for reliable PORT handling
CMD ["python", "/app/start.py"]
