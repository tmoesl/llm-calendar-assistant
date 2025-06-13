#!/bin/bash
set -euo pipefail
IFS=$'\n\t'


# Flower Monitoring Startup for Docker
echo "🚀 Starting Flower Monitoring Dashboard..."
echo "🔧 REDIS Host: $REDIS_HOST"
echo "🔧 REDIS Port: $REDIS_PORT"
echo "🔧 Flower Port: $FLOWER_PORT"
echo "🔧 Redis_DB: $REDIS_DB"
echo ""

# Flower Command (using default task columns)
CMD=("celery" "--broker=redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB" "flower" "--port=5555" "--auto_refresh=True")

# Execute
exec "${CMD[@]}"


