# 🤖 LLM Calendar Assistant

<p style="text-align: left;">
    <img src="https://img.shields.io/badge/-Completed-34A853?style=flat&label=Project&labelColor=23555555" alt="Status">
    <img src="https://img.shields.io/github/languages/count/tmoesl/llm-calendar-assistant?label=Languages" alt="GitHub language count">
    <img src="https://img.shields.io/github/languages/top/tmoesl/llm-calendar-assistant?color=white" alt="GitHub top language">
</p>


The LLM Calendar Assistant isn't just another calendar tool – it's your shortcut to a production-ready AI-powered calendar infrastructure. Built for speed and control, its modular architecture brings together the best AI models and design patterns to help you deploy faster without compromising flexibility.

Transform calendar operations from complex UI interactions to simple conversations:
- *"Schedule a team meeting tomorrow at 3pm about AWS re:Inforce"* → Creates event
- *"Cancel my 2pm call today"* → Finds and deletes event  

## ⭐ What Makes This Special

### 🤖 **AI-Powered Calendar Operations**
- **Natural Language Processing**: Translates human requests into calendar actions
- **Multi-LLM Support**: Works with OpenAI GPT-4 and Anthropic Claude
- **Structured LLM Output**: Pydantic schemas ensure reliable data extraction
- **Prompt Engineering**: Jinja2 templating for versioned, maintainable prompts

### 🏗️ **Production-Ready Architecture**
- **FastAPI & SQLAlchemy**: Modern Python backend with robust data handling
- **Celery & Redis**: Background task processing for responsive user experience
- **PostgreSQL (Supabase)**: Reliable event storage with free tier support
- **Docker**: One-command deployment with automatic migrations and health checks

### 🔧 **Developer Experience**
- **Modular & Scalable**: Add, extend, or customize components as needs grow
- **Real-time Monitoring**: Flower dashboard for background task visibility
- **Google Calendar Integration**: Full OAuth2 authentication and API integration
- **Comprehensive Logging**: Built-in monitoring and security best practices

## ⚡️ System Architecture

![Architecture Diagram](https://placehold.co/800x400)

### Request Flow
1. **API Ingestion**: FastAPI receives and validates requests
2. **Database Storage**: Events stored with unique IDs
3. **Queue Processing**: Celery queues background processing
4. **AI Pipeline**: Multi-stage LLM processing pipeline
5. **Calendar Integration**: Google Calendar API operations
6. **Result Storage**: Processing results stored in database

### Processing Pipeline Stages
| Stage | Purpose | AI Model Usage |
|-------|---------|----------------|
| **Validation** | Security and input sanitization | Rule-based |
| **Classification** | Intent detection (create/delete) | LLM |
| **Routing** | Direct to appropriate handler | Rule-based |
| **Extraction** | Extract event details from natural language | LLM |
| **Execution** | Perform Google Calendar operations | API calls |

## 🚀 Getting Started

Ready to deploy your AI calendar assistant? Get up and running in under a few minutes:

**Tech Prerequisites**
- Docker (20.10+) and Docker Compose (2.0+)
- UV (Python package manager)
- Python (3.12.8+)

**Service Prerequisites**
- PostgreSQL Database ([Supabase](https://supabase.com/) free tier supported)
- LLM Provider API Keys ([OpenAI Platform](https://platform.openai.com/) or [Anthropic Console](https://console.anthropic.com/))
- Google Calendar API Credentials ([Google Cloud Console](https://console.cloud.google.com/))

### Quick-Start

Before you begin, make sure the Docker Daemon is running, all prerequisites are installed, and required credentials are available.
```bash
# 1. Clone Repository
git clone https://github.com/yourusername/llm-calendar-assistant.git
cd llm-calendar-assistant

# 2. Set Up Environment
uv venv --python 3.12.8
source .venv/bin/activate
uv sync

# 3. Configure Environment Variables
cp .env.sample .env

# 4. Initiate OAuth Token
./scripts/init_token.sh

# 5. Start Application
./docker/start.sh [--dev]
```

**📖 [Complete Setup Guide →](docs/quick-start.md)**

## 🌐 Service Access

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | http://localhost:8080 | REST endpoints |
| **Docs** | http://localhost:8080/docs | Swagger UI |
| **Flower** | http://localhost:5555 | Task monitoring (dev only) |

## 📁 Project Structure

The codebase follows a clean, modular structure for building event-driven GenAI applications.
```
├── alembic/                   # Database migration scripts
├── app/
│   ├── api/                   # API endpoints and routers
│   ├── calendar/              # Google Calendar integration
│   ├── core/                  # Core components for workflow and task processing
│   ├── database/              # Database models and utilities
│   ├── llm/                   # LLM providers and services
│   ├── logging/               # Logging configuration and factory
│   ├── middleware/            # FastAPI middleware components
│   ├── pipeline/              # LLM processing pipeline
│   ├── prompts/               # Jinja2 prompt templates for AI models
│   ├── services/              # Business logic and utility services
│   ├── shared/                # Shared utilities and helpers
│   ├── worker/                # Celery background task definitions
│   └── main.py                # FastAPI application entry point
├── docker/                    # Docker configuration and scripts
├── docs/                      # Documentation and guides
├── scripts/                   # Shell scripts for operations
```

## 📚 Documentation

- **[Quick Start Guide](docs/quick-start.md)**: Complete setup and deployment instructions
- **[Service Setup Guide](docs/service-setup.md)**: Setup instructions for Supabase, LLM providers, and Google Calendar
- **[Docker Operations Guide](docker/README.md)**: Docker-specific management and troubleshooting
- **[API Patterns](docs/api-patterns.md)**: Development patterns and architecture details
- **[Development Patterns](docs/development-patterns.md)**: Code patterns and architectural guidelines

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
