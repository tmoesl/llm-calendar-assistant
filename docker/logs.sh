#!/bin/bash
set -e

echo "📋 LLM Calendar Assistant - Service Logs"
echo ""

# Environment validation and loading
if [[ ! -f ".env" ]]; then
    echo "❌ Missing .env file"
    exit 1
fi

source ./.env
echo "✅ Project: $PROJECT_NAME"

# Service selection and log display
SERVICE=${1:-}
if [[ -n "$SERVICE" ]]; then
    echo "📋 Showing logs for: $SERVICE"
    echo ""
    
    # Check if service exists and is running
    if docker compose -p "$PROJECT_NAME" ps --services --filter "status=running" | grep -q "^${SERVICE}$"; then
        docker compose -p "$PROJECT_NAME" logs -f "$SERVICE"
    else
        echo "❌ Service '$SERVICE' not found or not running"
        echo "🔍 Running services: $(docker compose -p "$PROJECT_NAME" ps --services --filter "status=running" | tr '\n' ' ')"
    fi
else
    echo "📋 Showing logs for all running services..."
    echo ""
    docker compose -p "$PROJECT_NAME" logs -f 
fi