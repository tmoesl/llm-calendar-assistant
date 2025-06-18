#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# FastAPI Application Startup for Docker
echo "🚀 Starting FastAPI Application..."
echo "🔧 Binding: 0.0.0.0:8080 (internal)"
echo "🔧 Reload: disabled (production)"
echo ""

# Database Migrations
echo "📋 Running database migrations..."
alembic upgrade head
echo "✅ Database migrations completed"

# Uvicorn Command (reload is disabled in production)
CMD=("uvicorn" "app.main:app" "--host=0.0.0.0" "--port=8080")

# Execute
exec "${CMD[@]}" 