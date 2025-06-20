# Docker Operations Guide

Docker-specific management commands for the LLM Calendar Assistant.

> 📖 **Setup Instructions**: See the main [README.md](../README.md#-quick-start) for complete environment setup, prerequisites, and initial configuration.

## 🏗️ Container Architecture

- **Redis**: Message broker and task queue
- **API**: FastAPI application server  
- **Celery**: Background task workers (auto-scaling)
- **Flower**: Task monitoring dashboard (development only)

## 🚀 Management Commands

### Start Services
```bash
./docker/start.sh                   # Production mode
./docker/start.sh --dev             # Development with monitoring
```

### View Logs
```bash
./docker/logs.sh                    # All services
./docker/logs.sh api                # Specific service (api, celery, redis, flower)
```

### Stop Services
```bash
./docker/stop.sh                    # Normal stop
./docker/stop.sh --clean            # Stop + cleanup volumes
```

## 🌐 Service Access

| Service | URL | Purpose |
|---------|-----|---------|
| **API** | http://localhost:8080 | REST endpoints |
| **Health Check** | http://localhost:8080/api/v1/health | System status |
| **API Docs** | http://localhost:8080/docs | Swagger UI |
| **API Docs** | http://localhost:8080/redoc | ReDoc |
| **Flower** | http://localhost:5555 | Task monitoring (dev only) |

## 🔍 Health & Status

```bash
# Quick health check
curl http://localhost:8080/api/v1/health

# Full system check
curl "http://localhost:8080/api/v1/health/ready?check_flower=true"

# Container status
docker compose ps
```

## 🐛 Docker Troubleshooting

```bash
# Check container status
docker compose ps

# View specific service logs with recent history
./docker/logs.sh <service_name>

# Restart specific service
docker compose restart <service_name>

# Check Docker configuration
docker compose config

# Resource usage
docker compose stats

# Inspect OAuth token in named volume
docker compose exec api cat /app/tokens/token.json
```

## ⚙️ Docker-Specific Configuration

Key Docker settings in `.env`:

| Setting | Default | Purpose |
|---------|---------|---------|
| `API_PORT` | `8080` | Host port for API access |
| `REDIS_PORT` | `6379` | Host port for Redis access |
| `FLOWER_PORT` | `5555` | Host port for Flower dashboard |
| `CELERY_CONCURRENCY` | `2` | Workers per container |

These are external host port mappings - internal container ports and hostnames are fixed.

> 📝 **Complete Configuration**: See [README.md](../README.md#2-environment-setup) for all environment variables including database, LLM, and calendar settings.

## 📊 Scaling Workers

Adjust worker concurrency in `.env`:
```bash
CELERY_CONCURRENCY=4    # 4 workers per container
```

Then restart:
```bash
docker compose restart celery
```