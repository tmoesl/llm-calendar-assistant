# 🚀 Quick Start Guide

Complete setup walkthrough to get your LLM Calendar Assistant running in under 10 minutes.

**Prerequisites**: Review [tech and service requirements](../README.md#-getting-started) before starting.

## Step-by-Step Setup

### 1. Clone & Environment Setup
```bash
git clone https://github.com/yourusername/llm-calendar-assistant.git
cd llm-calendar-assistant

# Create virtual environment and install dependencies
uv venv --python 3.12.8
source .venv/bin/activate
uv sync
```

### 2. Service Configuration
```bash
# Copy environment template
cp .env.sample .env
```

Edit `.env` with your service credentials:
- **Database**: Add your Supabase connection string
- **LLM Provider**: Add OpenAI or Anthropic API key  
- **Google Calendar**: Ensure `credentials.json` is in project root

**Detailed service setup**: See [Service Setup Guide](service-setup.md)

### 3. OAuth Token Generation
```bash
# Generate initial OAuth token
./scripts/init_token.sh
```
Follow the browser prompts to authorize Google Calendar access.

### 4. Application Startup
```bash
# Production mode
./docker/start.sh

# Development mode (with monitoring)
./docker/start.sh --dev
```

### 5. Verification & Testing
```bash
# Check system health
curl http://localhost:8080/api/v1/health/ready

# Verify services are running
docker compose ps
```

All services should show "healthy" status.

## First API Call

### API Request
Test your setup with a calendar operation:

```bash
curl -X POST "http://localhost:8080/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Schedule a team meeting tomorrow at 2pm"
  }'
```

### Expected Response
```json
{
  "message": "Event accepted for processing",
  "task_id": "c4da7533-8895-4f5b-8d60-508e7b5fc79f",
  "event_id": "8c9dc692-846c-4074-93c6-c4ae5f91a4e6"
}
```

### Monitor Processing
Watch the request flow through your system:

```bash
# Watch API request handling
./docker/logs.sh api

# Watch Celery task execution
./docker/logs.sh celery
```

You should see logs showing the event classification, extraction, and Google Calendar API calls.

### Verify Database Entry
Check that the event was stored:

- **Supabase Dashboard**: Navigate to your events table to see the new entry
- **Terminal Query**: Use your database client to verify the event_id exists

## Next Steps

Your LLM Calendar Assistant is ready! Continue with:

- **[API Documentation](http://localhost:8080/docs)** - Interactive API testing
- **[Docker Operations Guide](../docker/README.md)** - Container management and scaling  
- **[Development Patterns](development-patterns.md)** - Code patterns and architectural guidelines

**Troubleshooting**: See [Service Setup Guide](service-setup.md) for service-specific issues. 

---