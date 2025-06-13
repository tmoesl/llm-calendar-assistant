#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Celery Worker Startup for Docker
echo "🚀 Starting Celery Worker..."
echo "🔧 REDIS Host: $REDIS_HOST"
echo "🔧 REDIS Port: $REDIS_PORT"
echo "🔧 CELERY Concurrency: $CELERY_CONCURRENCY"
echo "🔧 CELERY Log Level: $CELERY_LOG_LEVEL"
echo ""

# Celery Command (concurrency and loglevel handled by WorkerConfig)
CMD=("celery" "-A" "app.worker.start_worker:app" "worker")

# Execute
exec "${CMD[@]}"