# 🛠️ Local Development Guide

Set up the LLM Calendar Assistant for local development using a hybrid approach:
- 🐳 Docker for infrastructure (Redis, Flower)
- 🐍 Native Python for application services (FastAPI, Celery)
- ⚡ UV for fast and reproducible package manager and command execution

This setup offers the best of both worlds: isolated infrastructure without complex local installs, and fast iteration with native execution, hot reloads, and full debugger support


## 🔧 Prerequisites

Before you begin, ensure you have:

- **Docker Engine** ≥ 20.10 (for infrastructure services)
- **Python** ≥ 3.12 (for application services)  
- **uv** package manager (installed automatically with setup)
- **Supabase** project with credentials
- **Google Calendar** OAuth2 credentials

## ⚙️ Initial Setup

### 1. Environment Preparation

```bash
# Create virtual environment and install dependencies
uv venv
uv pip install -e .
```

### 2. Configuration Setup

```bash
# Copy environment template
cp env.sample .env

# Edit .env and set variables marked with 🔧 Must Set:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY  
# - DATABASE_HOST
# - DATABASE_PASSWORD
# - DATABASE_USER
```

### 3. Google Calendar Setup

1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Create OAuth2 credentials (Desktop application)
4. Download `credentials.json` to project root
5. `token.json` will be auto-generated on first API use

### 4. Database Initialization

```bash
# Run database migrations
make migrate
```

## 🚀 Development Workflow

**Quick Start:**
```bash
make dev      # Start Redis and show next steps
```

**Recommended Workflow:**
```bash
# Terminal 1: Start Redis
make redis    

# Terminal 2: Start background worker  
make celery   

# Terminal 3: Start API server  
make api      

# Terminal 4: Start monitoring
make flower   
```

**Startup Order**: Redis → Celery → API → Flower (health-checked dependencies ensure proper initialization)

**Check Status:**
```bash
make status   # Verify all services
```

## 🔧 Development Utilities

### Service Management
```bash
make stop         # Stop all services (preserves data)
make clean        # Stop all services and remove all containers & data
make logs         # Show application logs (real-time)
make help         # Show all available commands
make status       # Health check all services
```

### Database Operations
```bash
make makemigration  # Create new migration
make migrate        # Apply migrations
```

## 🌐 Service Access Points

Once all services are running, you can access:

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | http://localhost:8080 | Main application API |
| **API Docs** | http://localhost:8080/docs | Interactive API documentation |
| **Health Check** | http://localhost:8080/api/v1/health | Service health status |
| **Flower Dashboard** | http://localhost:5555 | Celery task monitoring |


## 💡 Tips

- **Hot Reload**: API changes reflect immediately with `--reload`
- **Task Monitoring**: Use Flower dashboard for Celery tasks
- **Service Management**: `make stop` preserves data, `make clean` removes all containers & data
- **Environment**: Use `uv run` commands (no activation needed)
- **Token Persistence**: token.json is auto-saved after first calendar access

## 🐛 Troubleshooting

**Services:**
```bash
make status             # Check all services
make logs               # View logs  
make clean && make dev  # Reset everything
```

**Port conflicts:**
```bash
lsof -i :8080  # API
lsof -i :6379  # Redis
lsof -i :5555  # Flower
```
---