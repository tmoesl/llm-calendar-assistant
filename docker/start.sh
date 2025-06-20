#!/bin/bash
set -e

echo "🚀 LLM Calendar Assistant - Docker Setup"
echo ""

# Environment validation and loading
if [[ ! -f ".env" ]]; then
    echo "❌ Missing .env file"
    echo "   Run: cp env.sample .env"
    echo "   Then configure: DATABASE_HOST, DATABASE_PASSWORD, OPENAI_API_KEY"
    exit 1
fi

source ./.env
echo "✅ Project: $PROJECT_NAME"

# OAuth token check (optional - Docker named volume handles this)
if [[ -f "token.json" ]]; then
    echo "ℹ️  Host token.json found - consider: ./scripts/init_token.sh"
fi

# Profile determination
if [[ "$1" == "--dev" ]]; then
    echo "🔧 Starting DEVELOPMENT mode (hot reload + monitoring)"
    PROFILE="dev"
else
    echo "🚀 Starting PRODUCTION mode"
    PROFILE="prod"
fi

echo ""
echo "📦 Building and starting containers..."
docker compose -p "$PROJECT_NAME" --profile "$PROFILE" up --build -d

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🔗 Access Points:"
echo "   API:          http://localhost:$API_PORT"
echo "   API Docs:     http://localhost:$API_PORT/docs"
echo "   API Docs:     http://localhost:$API_PORT/redoc"

if [[ "$PROFILE" == "dev" ]]; then
    echo "   Flower:       http://localhost:$FLOWER_PORT"
fi 