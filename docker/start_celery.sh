#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Celery Worker Startup for Docker
echo "🚀 Starting Celery Worker..."
echo "🔧 Broker: redis://$REDIS_HOST:6379/0 (internal)"
echo "🔧 Concurrency: $CELERY_CONCURRENCY workers"
echo "🔧 Log Level: $CELERY_LOG_LEVEL"
echo ""

# Celery Command (concurrency and loglevel handled by WorkerConfig)
CMD=("celery" "-A" "app.worker.start_worker:app" "worker")

# Execute
exec "${CMD[@]}"