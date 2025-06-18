# Docker Setup Guide

Streamlined Docker management for the LLM Calendar Assistant.

## 🏗️ Container Architecture

- **Redis**: Message broker and result backend (persistent storage)
- **API**: FastAPI application server (health checks, REST endpoints)  
- **Celery**: Background task workers (scalable replicas and concurrency)
- **Flower**: Optional monitoring dashboard (worker stats, task history)

**Startup Order**: Redis → Celery → API → Flower (health-checked dependencies ensure proper initialization)

## 🌐 Access Points

- **API Health**: http://localhost:8080/api/v1/health
- **API Docs**: http://localhost:8080/docs
- **Flower Dashboard**: http://localhost:5555 (with `--monitoring`)

## 🔧 Environment Configuration

**Layered approach:** `.env` (baseline) + `.env.docker` (container overrides)

| Setting | Development | Container |
|---------|-------------|-----------|
| `REDIS_HOST` | `localhost` | `redis` |
| `LOG_LEVEL` | `DEBUG` | `INFO` |
| `CELERY_LOG_LEVEL` | `DEBUG` | `INFO` |

## 🚀 Management Commands

### Start
```bash
./docker/start.sh                   # Production startup (recommended)
./docker/start.sh --quick           # Fastest startup
./docker/start.sh --monitoring      # Include monitoring
./docker/start.sh --verbose         # Show detailed progress
```

### Logs
```bash
./docker/logs.sh              # All logs (last 50 lines)
./docker/logs.sh api -f       # Follow API logs
./docker/logs.sh celery       # Worker logs
```

### Stop
```bash
./docker/stop.sh               # Clean stop (recommended)
./docker/stop.sh --quick       # Fastest stop
./docker/stop.sh --cleanup     # For network issues
./docker/stop.sh --all         # Fresh start
```

## 🔍 Health Monitoring

```bash
# API health check
docker compose -p llm-calendar-assistant exec api curl -s http://localhost:8080/api/v1/health

# Celery health check
docker compose -p llm-calendar-assistant exec celery celery -A app.worker.start_worker:app inspect ping

# Redis health check
docker compose -p llm-calendar-assistant exec redis redis-cli ping

# Flower health check
docker compose -p llm-calendar-assistant exec flower curl -s http://localhost:5555 | grep -q "Flower" && echo "Flower is running!"

# Container status
docker compose -p llm-calendar-assistant ps

# Resource usage
docker compose -p llm-calendar-assistant stats

# 
```

## 🐛 Troubleshooting

```bash
# Startup issues
./docker/start.sh --verbose
./docker/logs.sh <service> --tail 50

# Configuration
docker compose -p llm-calendar-assistant config

# Google Calendar credentials
docker compose -p llm-calendar-assistant exec celery ls -la credentials.json token.json
```

## 📊 Scaling

```bash
# Horizontal: Configure worker containers (hardcoded: 2 replicas)
# Edit docker-compose.yml: replicas: 2
docker compose up -d

# Vertical: Configure workers per container  
# Edit .env: CELERY_CONCURRENCY=8
docker compose restart celery

# Result: 2 containers × 8 workers = 16 concurrent tasks
```