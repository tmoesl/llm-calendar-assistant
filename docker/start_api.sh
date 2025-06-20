#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

echo "🚀 FastAPI Application - Container Startup"
echo ""

# Database Migrations
echo "📋 Running database migrations..."
alembic upgrade head
echo "✅ Database migrations completed"
echo ""

# Determine runtime mode (check if source code is mounted for hot reload)
if [[ -w "/app/app" ]]; then
    echo "🔧 Development mode: Hot reload enabled"
    echo "🔧 Binding: 0.0.0.0:8080 (internal)"
    CMD=("uvicorn" "app.main:app" "--host=0.0.0.0" "--port=8080" "--reload")
else
    echo "🚀 Production mode: Optimized startup"
    echo "🔧 Binding: 0.0.0.0:8080 (internal)"
    CMD=("uvicorn" "app.main:app" "--host=0.0.0.0" "--port=8080")
fi

echo ""
echo "▶️  Starting server..."
exec "${CMD[@]}" 