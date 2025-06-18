#!/bin/bash
set -euo pipefail
IFS=$'\n\t'


# Flower Monitoring Startup for Docker
echo "🚀 Starting Flower Monitoring Dashboard..."
echo "🔧 Broker: redis://$REDIS_HOST:6379/0 (internal)"
echo "🔧 Binding: 0.0.0.0:5555 (internal)"

echo ""

# Flower Command (using default task columns)
CMD=("celery" "--broker=redis://$REDIS_HOST:6379/0" "flower" "--host=0.0.0.0" "--port=5555" "--auto_refresh=True")  # Fixed port/DB for internal communication

# Execute
exec "${CMD[@]}"


