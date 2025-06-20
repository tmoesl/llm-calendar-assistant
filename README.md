# 🤖 LLM Calendar Assistant

The LLM Calendar Assistant isn't just another calendar tool – it's your shortcut to a production-ready AI-powered calendar infrastructure. Built for speed and control, its modular architecture brings together the best AI models and design patterns to help you deploy faster without compromising flexibility.

Transform calendar operations from complex UI interactions to simple conversations:
- *"Schedule team meeting tomorrow at 3pm"* → Creates event
- *"Cancel my 2pm call today"* → Finds and deletes event  
- *"What's on my calendar next week?"* → Shows upcoming events

## 🚀 Core Tech Stack

- **FastAPI**: Modern Python API backend
- **Celery & Redis**: Background task queue and fast job processing
- **PostgreSQL**: Robust event and data storage (Supabase recommended)
- **LLMs**: Pluggable LLM providers for natural language processing
- **Docker**: Containerized deployment for consistent dev and production environments
- **Flower**: Real-time monitoring dashboard for background tasks

## ⭐ Key Features

- **Natural Language Processing**: Built-in support for converting human requests into calendar actions
- **Multi-LLM Support**: Works with both OpenAI GPT-4 and Anthropic Claude
- **Modular & Scalable**: Add, extend, or customize components as your needs grow
- **Production-Ready**: Includes logging, monitoring, and security best practices
- **Easy Deployment**: One-command startup with Docker, automatic migrations, and health checks
- **Google Calendar Integration**: Full OAuth2 authentication and API integration included

## ⚡️ Event-Driven Architecture
All interactions follow a unified event processing pipeline:
- Events are received via FastAPI endpoints
- Persisted in PostgreSQL
- Enqueued in Redis
- Processed by Celery workers
- Results written back to the database
- Optional: Callbacks notify external systems

## 🚀 Quick Start

### Prerequisites
- **Docker** (version 20.10+) and **Docker Compose** (version 2.0+)
- **Git** for cloning the repository
- **PostgreSQL Database** (Supabase recommended for quick setup)
- **LLM Provider API Keys** (at least one required): [OpenAI Platform](https://platform.openai.com/) or [Anthropic Console](https://console.anthropic.com/)

### 1. Clone and Navigate to Repository

```bash
# Clone the repository
git clone https://github.com/tmoesl/llm-calendar-assistant.git
cd llm-calendar-assistant
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.sample .env
```

Edit the `.env` file with your configuration:
- **Database**: DATABASE_HOST, DATABASE_PASSWORD, DATABASE_USER
- **LLM Provider**: OPENAI_API_KEY, ANTHROPIC_API_KEY
- **User Timezone**: CALENDAR_USER_TIMEZONE

### 3. Google Calendar Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable the Google Calendar API**:
   - Go to "APIs & Services" → "Library", search and enable "Google Calendar API"

3. **Create OAuth 2.0 Credentials**:
   - "APIs & Services" → "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Download the credentials.json file and place it in your project root

4. **Generate OAuth Token**:
   ```bash
   # Install dependencies (if not using Docker)
   uv sync
   
   # Run OAuth flow to get token.json
   python get_token.py
   ```

5. **Migrate Token to Docker** (if you have existing token.json):
   ```bash
   # Copy existing token to Docker named volume
   ./docker/migrate_token.sh
   ```

### 6. Start Services

```bash
# Production deployment
./docker/start.sh

# Development mode (with hot reload + monitoring)
./docker/start.sh --dev
```

This command will automatically:
- Build all Docker containers
- Start services via docker-compose
- Run database migrations
- Enable hot reload in development mode

## ✅ Verification

### Check Container Status
```bash
# Verify all containers are running
docker compose ps
```

### Test API Health
```bash
# Basic health check
curl http://localhost:8080/api/v1/health

# Full system check (including Flower if enabled)
curl http://localhost:8080/api/v1/health/ready?check_flower=true
```

### Test Calendar Integration
```bash
# Submit a natural language event request
curl -X POST http://localhost:8080/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{"request": "Schedule team standup tomorrow at 9am"}'

# Expected response: {"task_id": "abc-123", "event_id": "evt-456"}
```

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | http://localhost:8080 | Main application endpoints |
| **Interactive Docs** | http://localhost:8080/docs | Swagger UI for testing |
| **API Documentation** | http://localhost:8080/redoc | ReDoc documentation |
| **Flower Dashboard** | http://localhost:5555 | Task monitoring (if enabled) |
| **Health Check** | http://localhost:8080/api/v1/health | System status |

🎉 **Success!** Your LLM Calendar Assistant is now running and ready to process natural language calendar requests.

## 📋 Management

### View Logs
```bash
# View all service logs
./docker/logs.sh

# View specific service logs
./docker/logs.sh api
```

### Stop Services
```bash
# Stop all services
./docker/stop.sh

# Stop all services and clean up volumes/networks
./docker/stop.sh --clean
```

## 📚 Documentation

For detailed Docker management and troubleshooting, see the [Docker Setup Guide](docker/README.md).

**Additional Guides**: [Development Guide](docs/development.md) | [API Patterns](docs/api-patterns.md) | [Configuration](docs/configuration-patterns.md)

## 📁 Project Structure

The project follows a logical, scalable, and reasonably standardized project structure for building AI-powered calendar applications.

```
├── alembic              # Database migration scripts
├── app
│   ├── api              # API endpoints and routers
│   ├── calendar         # Google Calendar integration
│   ├── core             # Core components for workflow and task processing
│   ├── database         # Database models and utilities
│   ├── llm              # LLM providers and services
│   ├── logging          # Logging configuration and utilities
│   ├── middleware       # Middleware for request/response processing
│   ├── pipeline         # LLM processing pipeline
│   ├── prompts          # Prompt templates for AI models
│   ├── services         # Service definitions and integrations
│   ├── shared           # Shared utilities and components
│   └── worker           # Background task definitions
├── docker               # Docker configuration files
├── docs                 # Documentation and guides
└── tests                # Test definitions and handlers
```
