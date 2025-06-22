# Docker Operations Guide

Complete operations guide for managing your containerized LLM Calendar Assistant deployment.

**Prerequisites**: Complete the [Main Setup Guide](../README.md#-getting-started) and [Service Setup Guide](../docs/service-setup.md) before using these Docker commands.

## 🏗️ Container Architecture

### Service Overview
The application runs as a multi-container setup with environment-specific naming:

- **Redis**: Message broker and task queue
- **API**: FastAPI application server  
- **Celery**: Background task workers (auto-scaling)
- **Flower**: Task monitoring dashboard (development only)

All services are fully containerized with Docker, ensuring a consistent experience across development and production. Service names adapt to the environment (e.g., api / api-dev, celery / celery-dev).

### Service Images
The system uses a hybrid approach for container images to balance reliability with customization:

- **Redis**: Prebuilt official image (`redis:latest`)
- **API/Celery/Flower**: Custom multi-stage Dockerfiles (builder → production stages, non-root users)

### Persistent Storage
Critical data is preserved through named volumes to ensure system continuity and enable container coordination:

- **`redis_data`**: Persists message queue and task results across container restarts
- **`token_data`**: Shared OAuth tokens between API and Celery containers with automatic refresh and corruption-safe multi-container access

### Docker Profiles
Profiles enable environment-specific service deployment, controlling which containers start based on your operational needs:

- **Always started**: Redis (no profiles key)
- **Profile-specific**: API/Celery (dev/prod), Flower (dev)


## 🚀 Operations

### Start/Stop Services
```bash
./docker/start.sh [--dev]           # Start (production/development)
./docker/stop.sh [--clean]          # Stop (normal/cleanup volumes)
```

### Logs
```bash
./docker/logs.sh                    # View logs (all active services)
./docker/logs.sh [service]          # View logs (specfic service only)
```

### Performance Monitoring
```bash
docker compose ps                   # Container status
docker stats --no-stream            # Resource usage
```

### Container Access
```bash
docker compose exec [service] bash  # Access service container
```

## 🌐 Service Access

| Service | URL | Purpose | Mode |
|---------|-----|---------|------|
| **API** | http://localhost:8080 | REST endpoints | Both |
| **API Docs** | http://localhost:8080/docs | Swagger UI | Both |
| **Flower** | http://localhost:5555 | Task monitoring | Dev only |

## 🔍 Health Checks

```bash
# Basic health check
curl http://localhost:8080/api/v1/health

# Full system check (production)
curl http://localhost:8080/api/v1/health/ready

# Full system check (development - includes Flower)
curl "http://localhost:8080/api/v1/health/ready?check_flower=true"
```

## ⚙️ Configuration

### Environment Variables
**Port Configuration** - Internal container ports are fixed. Only external host ports are configurable:

| Setting | Default | Purpose |
|---------|---------|---------|
| `API_PORT` | `8080` | External host port for API access |
| `REDIS_PORT` | `6379` | External host port for Redis access |
| `FLOWER_PORT` | `5555` | External host port for Flower dashboard |

## 📊 Scaling & Performance

### Worker Scaling
```bash
# Horizontal scaling: More worker containers
docker compose up --scale celery=3 -d

# Vertical scaling: More threads per container
# Edit .env: CELERY_CONCURRENCY=4, then restart
docker compose restart celery
```

## 🐛 Troubleshooting

### Container Issues
```bash
# Check configuration
docker compose config

# View detailed logs
./docker/logs.sh

# Check available ports
ss -tlnp | grep -E '(8080|6379|5555)'
```

### Connectivity Issues
```bash
# Test system health (Database, Redis, Celery, Flower)
curl http://localhost:8080/api/v1/health/ready

# Test with Flower (dev mode)
curl "http://localhost:8080/api/v1/health/ready?check_flower=true"
```

### Performance Issues
```bash
# Check resource usage
docker stats --no-stream

# Reduce worker concurrency
# Edit .env: CELERY_CONCURRENCY=1
docker compose restart celery
```

### OAuth Token Issues
```bash
# Reinitialize token (most common solution)
./scripts/init_token.sh

# Check token content
docker compose exec api cat /app/tokens/token.json

# Check token in container (adjust container name for mode)
docker compose exec api-dev ls -la /app/tokens/

# Clear corrupted token (rare)
docker compose exec api sh -c 'echo "" > /app/tokens/token.json'
```

**Note**: OAuth tokens are shared between containers via Docker named volumes (`token_data`).

---

🔗 **Links**: [Main README](../README.md) | [Quick Start Guide](../docs/quick-start.md) | [Service Setup Guide](../docs/service-setup.md)