# 🛠️ Local Development Guide

Simple local development setup using a hybrid approach:
- 🐳 **Docker** for infrastructure (Redis, Flower)  
- 🐍 **Native Python** for development (FastAPI, Celery)
- ⚡ **Hot reload** and full debugger support

## 📋 Prerequisites

- **Initial setup completed** → See [README](../README.md)
- **Docker** → Installed and running

## 🚀 Quick Start

```bash
# 1. One command setup
make dev      # Start development (setup + health check)

# 2. Follow the instructions to start services in separate terminals:
make redis    # Terminal 1: Infrastructure
make celery   # Terminal 2: Background worker  
make api      # Terminal 3: API server
make flower   # Terminal 4: Monitoring (optional)
```


## 🌐 Access Points

> **Note:** URLs below use default ports from `env.sample`. If you've changed `API_PORT` or `FLOWER_PORT` in your `.env` file, adjust the URLs accordingly.

### Services
| Service | URL | Purpose |
|---------|-----|---------|
| **API** | http://localhost:8080 | Main application |
| **API Docs** | http://localhost:8080/docs | Interactive documentation |
| **Flower** | http://localhost:5555 | Task monitoring |

### API Service Endpoints
| Endpoint | Method | URL | Purpose |
|----------|--------|-----|---------|
| **Health** | GET | http://localhost:8080/api/v1/health | Basic health check |
| **Ready** | GET | http://localhost:8080/api/v1/health/ready | Service readiness check |
| **Auth Status** | GET | http://localhost:8080/api/v1/calendar/auth/status | Check calendar authentication |
| **Auth Revoke** | POST | http://localhost:8080/api/v1/calendar/auth/revoke | Revoke calendar authentication |

## 🔧 Commands

### Development Workflow
```bash
make dev           # Start development (setup + health check)
make status        # Check all services
```

### Services
```bash
make redis         # Start Redis
make celery        # Start Celery worker
make api           # Start FastAPI
make flower        # Start monitoring
```

### Database
```bash
make migrate       # Apply migrations
make makemigration # Create new migration
```

### Utilities
```bash
make logs          # View application logs
make stop          # Stop all services
make clean         # Stop and remove everything
make doctor        # System health check
```

**Common Issues:**
- Docker not running → Start Docker Desktop
- Port conflicts → Check `lsof -i :8080` (or :6379, :5555)
- Missing `.env` → Copy from `env.sample`

---

**💡 Tip:** Use `make help` to see all available commands