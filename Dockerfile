# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install numpy FIRST (before chromadb pulls numpy 2.0)
RUN pip install --no-cache-dir "numpy<2.0"

# Install all other packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create ChromaDB directory
RUN mkdir -p /app/chroma_data

EXPOSE 8000

CMD ["bash", "start.sh"]
