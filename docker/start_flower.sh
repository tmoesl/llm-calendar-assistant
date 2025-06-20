#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

echo "🚀 Flower Monitoring - Container Startup"
echo ""

echo "🔧 Configuration:"
echo "   Broker: redis://redis:6379/0 (internal)"
echo "   Binding: 0.0.0.0:5555 (internal)"
echo "   Auto Refresh: Enabled"
echo ""

# Flower Command (using default task columns)
CMD=("celery" "--broker=redis://redis:6379/0" "flower" "--host=0.0.0.0" "--port=5555" "--auto_refresh=True")

echo ""
echo "▶️  Starting dashboard..."
exec "${CMD[@]}"


