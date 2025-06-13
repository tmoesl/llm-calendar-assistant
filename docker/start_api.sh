#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# FastAPI Application Startup for Docker
echo "🚀 Starting FastAPI Application..."
echo "🔧 API Host:   $API_HOST"
echo "🔧 API Port:   $API_PORT"
echo "🔧 API Reload: $API_RELOAD"
echo ""

# Database Migrations
echo "📋 Running database migrations..."
alembic upgrade head
echo "✅ Database migrations completed"

# Uvicorn Command
CMD=("uvicorn" "app.main:app" "--host" "$API_HOST" "--port" "$API_PORT")
[ "$API_RELOAD" = "true" ] && CMD+=("--reload")

# Execute
exec "${CMD[@]}" 