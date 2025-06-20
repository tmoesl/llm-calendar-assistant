#!/bin/bash
set -e

echo "🛑 LLM Calendar Assistant - Stopping Services"
echo ""

# Environment validation and loading
if [[ ! -f ".env" ]]; then
    echo "❌ Missing .env file"
    exit 1
fi

source ./.env
echo "✅ Project: $PROJECT_NAME"

# Stop all profiles
echo "📦 Stopping containers..."
docker compose -p "$PROJECT_NAME" --profile dev --profile prod --profile monitoring down --timeout 0

# Optional cleanup
if [[ "$1" == "--clean" ]]; then
    echo ""
    echo "🧹 Cleaning volumes and networks..."
    docker compose -p "$PROJECT_NAME" down --volumes --timeout 0
    docker system prune -f
fi

echo ""
echo "✅ Services stopped successfully!" 