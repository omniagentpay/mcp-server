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

# Copy and extract omniagentpay from tar.gz (more reliable for Cloud Build)
COPY omniagentpay-0.0.1.tar.gz /tmp/
RUN mkdir -p /tmp/omniagentpay-extract && \
    tar -xzf /tmp/omniagentpay-0.0.1.tar.gz -C /tmp/omniagentpay-extract && \
    mkdir -p /usr/local/lib/python3.11/site-packages/omniagentpay && \
    cp -r /tmp/omniagentpay-extract/omniagentpay-0.0.1/omniagentpay/* /usr/local/lib/python3.11/site-packages/omniagentpay/

# Install Python dependencies
# Install omniagentpay dependencies first (from pyproject.toml), then other requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "circle-developer-controlled-wallets>=9.1.0" "pydantic>=2.12.0" "httpx>=0.28.0" "python-dotenv>=1.2.0" "cryptography>=44.0.0" "redis>=7.1.0" && \
    grep -v "^omniagentpay" requirements.txt > /tmp/requirements_filtered.txt && \
    pip install --no-cache-dir -r /tmp/requirements_filtered.txt

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
