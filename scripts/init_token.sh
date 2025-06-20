#!/bin/bash
set -e

echo "🔄 OAuth Token Initialization - Named Volume Setup"
echo ""

# Environment validation and loading
if [[ ! -f ".env" ]]; then
    echo "❌ Missing .env file"
    echo "   Run: cp env.sample .env"
    exit 1
fi

source ./.env
echo "✅ Project: $PROJECT_NAME"

# Check if token.json exists, generate if missing
if [[ ! -f "token.json" ]]; then
    echo "🔐 Generating OAuth token..."
    python -m app.services.init_token
    
    if [[ ! -f "token.json" ]]; then
        echo "❌ Token generation failed"
        exit 1
    fi
    echo "✅ Token generated successfully"
else
    echo "✅ Using existing token.json"
fi

# Start services to create the named volume
echo "🚀 Starting containers to create named volume..."
docker compose -p "$PROJECT_NAME" up --no-deps -d redis

# Wait a moment for volume creation
sleep 2

# Copy token.json to named volume via temporary container
echo "📤 Copying token.json to named volume..."
docker run --rm \
    -v "$(pwd)/token.json:/host/token.json:ro" \
    -v "${PROJECT_NAME}_token_data:/app/tokens" \
    alpine:latest cp /host/token.json /app/tokens/token.json

# Fix permissions on the token directory and file for container users
echo "🔧 Setting correct permissions..."
docker run --rm \
    -v "${PROJECT_NAME}_token_data:/app/tokens" \
    alpine:latest sh -c 'chown -R 999:999 /app/tokens && chmod 755 /app/tokens && chmod 644 /app/tokens/token.json'

echo ""
echo "✅ Initialization completed!"
echo "   • Host token.json copied to named volume at tokens/token.json"
echo "   • Directory and file permissions set for container users (UID:GID 999:999)"
echo "   • All containers will now use shared named volume"
echo "   • Your existing token.json is preserved on host as backup"
echo ""
echo "🚀 Ready to start services:"
echo "   ./docker/start.sh" 