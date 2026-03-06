#!/bin/bash
# start.sh — Startup script for Docker container

echo "🚀 Starting DocuMind..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 3

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Start the application
echo "✅ Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000