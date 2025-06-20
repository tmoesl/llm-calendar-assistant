#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

echo "🚀 Celery Worker - Container Startup"
echo ""

echo "🔧 Configuration:"
echo "   Broker: redis://redis:6379/0 (internal)"
echo "   Concurrency: ${CELERY_CONCURRENCY:-2} workers"
echo "   Log Level: ${CELERY_LOG_LEVEL:-INFO}"
echo ""

# Celery Command (actual concurrency and loglevel handled by WorkerConfig)
CMD=("celery" "-A" "app.worker.start_worker:app" "worker")

echo ""
echo "▶️  Starting worker..."
exec "${CMD[@]}"