# LLM Calendar Assistant

A production-ready microservice calendar assistant powered by Large Language Models, built with FastAPI, Celery, Redis, and Supabase.

## ✨ Features

- **FastAPI** web API with interactive documentation
- **Celery** background task processing  
- **Redis** message broker and caching
- **Supabase** PostgreSQL database with automatic migrations
- **Google Calendar** OAuth2 integration with automatic token management
- **Docker** containerization with streamlined scripts

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker Engine 20.10+
- Docker Compose 2.0+
- Supabase project credentials
- Google Calendar API credentials (OAuth2 client)

### Setup & Launch

```bash
# 1. Clone and navigate to project
git clone https://github.com/tmoesl/llm-calendar-assistant.git
cd llm-calendar-assistant

# 2. Create environment configuration  
cp env.sample .env
cp env.docker.sample .env.docker

# 3. Configure credentials in .env:
#    DATABASE_HOST=your_supabase_host.supabase.co
#    DATABASE_PASSWORD=your_supabase_password
#    OPENAI_API_KEY=sk-your-openai-key-here
#    ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# 4. Add Google Calendar OAuth2 credentials:
#    - Download credentials.json from Google Cloud Console
#    - Place in project root (token.json will be auto-generated)

# 5. Start services
./docker/start.sh
```

## 🔗 Access Points
- **API**: http://localhost:8080
- **Interactive Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/api/v1/health
- **Monitoring**: http://localhost:5555 (with `--monitoring`)

## 🛠️ Management

```bash
# Start services
./docker/start.sh                    # Full startup with health checks
./docker/start.sh --quick           # Fast startup, skip health checks  
./docker/start.sh --monitoring      # Include Flower monitoring dashboard

# View logs
./docker/logs.sh                    # All service logs
./docker/logs.sh api -f             # Follow API logs in real-time
./docker/logs.sh celery --tail 100  # Last 100 Celery worker logs

# Stop services
./docker/stop.sh                    # Clean shutdown (preserves data)
./docker/stop.sh --cleanup          # Remove containers and networks
./docker/stop.sh --all              # Nuclear cleanup (removes all data)
```

## 📁 Configuration

### Environment Files
- **`.env`**: Main configuration (copy from `env.sample`)
- **`.env.docker`**: Container overrides (copy from `env.docker.sample`)

### Required Credentials
- **Database**: `DATABASE_HOST`, `DATABASE_PASSWORD` (Supabase)
- **LLM APIs**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Google Calendar**: `credentials.json` file (OAuth2 client credentials)

### Google Calendar Setup
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Create OAuth2 credentials (Desktop application)
4. Download `credentials.json` to project root
5. First run will trigger OAuth flow and generate `token.json`

## 🏗️ Architecture

**Core Services:**
- **API Service**: FastAPI with automatic OpenAPI documentation
- **Worker Services**: 2x Celery workers for background calendar operations
- **Redis**: Message broker and caching with persistence
- **Monitoring**: Optional Flower dashboard for task monitoring

**External Integrations:**
- **Supabase**: Managed PostgreSQL database
- **OpenAI/Anthropic**: LLM providers for natural language processing
- **Google Calendar**: OAuth2-authenticated calendar operations

## 📖 Documentation

- **Setup Guide**: [docker/README.md](docker/README.md)
- **API Docs**: http://localhost:8080/docs
- **Environment Reference**: [env.sample](env.sample)