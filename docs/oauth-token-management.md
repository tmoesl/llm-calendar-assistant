# OAuth Token Management

This document explains how OAuth tokens are managed in the LLM Calendar Assistant using Docker named volumes.

## 🎯 Architecture Overview

### Named Volume Approach
- **token.json** is stored in a Docker named volume (`token_data`)
- All containers (API, Celery workers) share the same token file
- Atomic file operations ensure safe multi-container access
- Host interference is eliminated during runtime

### Volume Mapping
```yaml
volumes:
  token_data:/app/tokens  # Shared token directory across all containers
```

The token file is stored at `/app/tokens/token.json` within containers.

## 🚀 Setup Process

### 1. Initial Token Generation
```bash
# Generate token.json on host
python -m app.services.init_token
```

### 2. Initialize Token in Named Volume
```bash
# Copy host token to Docker named volume
./scripts/init_token.sh
```

### 3. Start Services
```bash
# Start with named volume
./docker/start.sh
```

## 🔄 Token Lifecycle

### Automatic Refresh
- Any container can refresh the OAuth token
- Atomic writes prevent corruption during multi-container access
- All containers immediately see refreshed tokens

### Manual Operations
```bash
# View current token
docker compose exec api cat /app/tokens/token.json

# Copy token from volume to host (backup)
docker compose exec api cat /app/tokens/token.json > backup-token.json

# Replace token in volume
echo '{"new": "token"}' | docker compose exec -T api tee /app/tokens/token.json
```

## 🔒 Security Benefits

1. **Container Isolation**: Token only accessible within Docker network
2. **No Host Interference**: Host can't accidentally modify token during runtime  
3. **Atomic Operations**: File corruption prevented with temp-file + replace pattern
4. **Multi-Container Safe**: Shared volume eliminates race conditions

## 🛠️ Troubleshooting

### Empty Token Volume
```bash
# Check if volume exists
docker volume ls | grep token_data

# Check token content
docker compose exec api cat /app/tokens/token.json

# Re-run initialization if needed
./scripts/init_token.sh
```

### Token Corruption
```bash
# Clear corrupted token
docker compose exec api sh -c 'echo "" > /app/tokens/token.json'

# Regenerate token
python -m app.services.init_token
./scripts/init_token.sh
```

### Multi-Container Issues
```bash
# Check which containers are accessing token
docker compose exec api ls -la /app/tokens/token.json
docker compose exec celery ls -la /app/tokens/token.json

# Restart all services to refresh connections
docker compose restart
```

## 📋 Migration from Bind Mounts

### Old Approach (Deprecated)
```yaml
volumes:
  - ./token.json:/app/token.json:rw  # ❌ Bind mount
```

### New Approach (Recommended)
```yaml
volumes:
  - token_data:/app/tokens           # ✅ Named volume
```

### Why Named Volumes are Better
- ✅ True atomic operations on native Linux filesystems
- ✅ No host/container race conditions  
- ✅ Multi-container safety guaranteed
- ✅ Consistent filesystem behavior
- ✅ Production-ready reliability 