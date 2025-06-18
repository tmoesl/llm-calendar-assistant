# =============================================================================
# LLM Calendar Assistant - Local Development (Hybrid Mode)
# =============================================================================

# Set timezone to UTC
export TZ=UTC

# -----------------------------------------------------------------------------
# Project Setup
# -----------------------------------------------------------------------------

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    DOCKER_HOST_FLAGS = --add-host=host.docker.internal:host-gateway
else
    DOCKER_HOST_FLAGS = 
endif

# Required environment file
ifeq (,$(wildcard .env))
$(error ".env file not found. Please create it or copy from .env.example")
endif
include .env
export

# Infrastructure ports and project name must be explicitly set in .env
REQUIRED_VARS := API_PORT FLOWER_PORT REDIS_PORT PROJECT_NAME
$(foreach var,$(REQUIRED_VARS),\
  $(if $(value $(var)),,$(error "$(var) not set in .env")))

# Container names
REDIS_CONTAINER=${PROJECT_NAME}_redis
FLOWER_CONTAINER=${PROJECT_NAME}_flower
REDIS_VOLUME=${PROJECT_NAME}_redis_data

# -----------------------------------------------------------------------------
# Dependency Checks
# -----------------------------------------------------------------------------

.PHONY: setup
setup:
	@echo "==== Project Setup ===="
	@printf "  Docker:   " ; docker info >/dev/null 2>&1 && echo "Running" || { echo "❌ Start Docker Desktop"; exit 1; }
	@printf "  Logs:     " ; mkdir -p logs && echo "Directory ready"
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""

.PHONY: doctor
doctor:
	@echo ""
	@echo "==== System Health Check ===="
	@echo "  Platform: $(UNAME_S)"
	@printf "  Docker:   " ; docker --version 2>/dev/null || echo "❌ Not found"
	@printf "  uv:       " ; uv --version 2>/dev/null || echo "❌ Not found"  
	@printf "  .env:     " ; test -f .env && echo "$(realpath .env)" || echo "❌ Missing"
	@printf "  Python:   " ; uv run python --version 2>/dev/null || echo "❌ Not available"
	@echo ""
	@echo "✅ System healthy!"
	@echo ""

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

.PHONY: help
help:
	@echo "==== Local Dev Commands (Hybrid Mode) ===="
	@echo "  make dev           - Start development"
	@echo "  make redis         - Start Redis"
	@echo "  make celery        - Start Celery worker"
	@echo "  make api           - Start FastAPI"
	@echo "  make flower        - Start Flower"
	@echo "  make status        - Check service status"
	@echo "  make logs          - Show application logs"
	@echo "  make stop          - Stop all services (preserves data)"
	@echo "  make clean         - Stop all services and remove all containers & data"
	@echo ""
	@echo "🔧 Troubleshooting:"
	@echo "  make doctor        - Check system health"
	@echo ""
	@echo "📊 Database:"
	@echo "  make migrate       - Apply migrations"
	@echo "  make makemigration - Create new migration"
	@echo ""
	@echo "🌐 Access:"
	@echo "  API:     http://localhost:$(API_PORT)"
	@echo "  Docs:    http://localhost:$(API_PORT)/docs"
	@echo "  Flower:  http://localhost:$(FLOWER_PORT)" 

# -----------------------------------------------------------------------------
# Infrastructure Services
# -----------------------------------------------------------------------------

.PHONY: redis
redis:
	@echo "==== Starting Redis ===="
	@if ! docker ps -f "name=$(REDIS_CONTAINER)" --format "{{.Names}}" | grep -q $(REDIS_CONTAINER); then \
		if ! docker ps -a -f "name=$(REDIS_CONTAINER)" --format "{{.Names}}" | grep -q $(REDIS_CONTAINER); then \
					docker run -d --name $(REDIS_CONTAINER) \
			-p $(REDIS_PORT):6379 \
				-v $(REDIS_VOLUME):/data \
				redis:latest redis-server --appendonly yes > /dev/null; \
		else \
			docker start $(REDIS_CONTAINER) > /dev/null; \
		fi; \
		sleep 2; \
		echo "✅ Redis started with persistent data"; \
	else \
		echo "✅ Redis already running"; \
	fi

.PHONY: flower
flower:
	@echo "==== Starting Flower ===="
	@echo "⏳ Waiting for Celery workers..."
	@timeout=30; \
	while [ $$timeout -gt 0 ]; do \
		if uv run celery -A app.worker.start_worker:app inspect ping > /dev/null 2>&1; then \
			echo "✅ Celery workers detected!"; \
			break; \
		fi; \
		sleep 2; \
		timeout=$$((timeout - 2)); \
	done; \
	if [ $$timeout -le 0 ]; then \
		echo "⚠️  Starting Flower without workers (will show warnings)"; \
	fi
	@if ! docker ps -f "name=$(FLOWER_CONTAINER)" --format "{{.Names}}" | grep -q $(FLOWER_CONTAINER); then \
		docker run -d --rm --name $(FLOWER_CONTAINER) -p $(FLOWER_PORT):5555 \
			$(DOCKER_HOST_FLAGS) \
			mher/flower:2.0 \
			celery --broker=redis://host.docker.internal:$(REDIS_PORT)/0 flower --host=0.0.0.0 --port=5555 --auto_refresh=True > /dev/null; \
		sleep 2; \
		echo "✅ Flower started"; \
	else \
		echo "✅ Flower already running"; \
	fi

# -----------------------------------------------------------------------------
# Application Services
# -----------------------------------------------------------------------------

.PHONY: celery
celery:
	@echo "==== Starting Celery worker ===="
	@uv run celery -A app.worker.start_worker:app worker

.PHONY: api
api:
	@echo "==== Starting FastAPI ===="
	@echo "📋 Running migrations..."
	@./migrate.sh
	@echo ""
	@echo "💻 Starting server..."
	@uv run uvicorn app.main:app --host=localhost --port=$(API_PORT) --reload

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

.PHONY: status
status:
	@echo "==== Service Status ===="
	@printf "  Redis:  " ; docker ps -f "name=$(REDIS_CONTAINER)" --format "{{.Names}}" | grep -q $(REDIS_CONTAINER) && echo "✅" || echo "❌"
	@printf "  Celery: " ; uv run celery -A app.worker.start_worker:app inspect ping > /dev/null 2>&1 && echo "✅" || echo "❌"
	@printf "  API:    " ; curl -s http://localhost:$(API_PORT)/api/v1/health > /dev/null 2>&1 && echo "✅" || echo "❌"
	@printf "  Flower: " ; docker ps -f "name=$(FLOWER_CONTAINER)" --format "{{.Names}}" | grep -q $(FLOWER_CONTAINER) && echo "✅" || echo "❌"

.PHONY: logs
logs:
	@echo "==== Application Logs ===="
	@tail -f logs/calendar_assistant.log 2>/dev/null || echo "No logs found. Start services to generate logs."

.PHONY: stop
stop:
	@echo "==== Stopping All Services ===="
	@echo "  • Docker containers"
	@docker stop $(REDIS_CONTAINER) $(FLOWER_CONTAINER) >/dev/null 2>&1 || true
	@echo "  • API processes"
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@echo "  • Worker processes"
	@pkill -f "celery.*app.worker.start_worker" 2>/dev/null || true
	@echo "✅ All services stopped"

.PHONY: clean
clean:
	@echo "==== Cleaning Everything ===="
	@echo "  • Docker containers"
	@docker rm -f $(REDIS_CONTAINER) $(FLOWER_CONTAINER) >/dev/null 2>&1 || true
	@echo "  • Docker volumes"
	@docker volume rm $(REDIS_VOLUME) >/dev/null 2>&1 || true
	@echo "  • API processes"
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@echo "  • Worker processes"
	@pkill -f "celery.*app.worker.start_worker" 2>/dev/null || true
	@echo "✅ All services stopped and cleaned"

.PHONY: dev
dev: setup doctor
	@echo ""
	@echo "==== Local Development Ready! ===="
	@echo "Next steps: Run in separate terminals"
	@echo "  make redis    # Redis"
	@echo "  make celery   # Celery worker" 
	@echo "  make api      # FastAPI server"
	@echo "  make flower   # Flower monitoring"
	@echo ""
	@echo "Quick check:"
	@echo "  make status   # Check service status"

# -----------------------------------------------------------------------------
# Database Operations
# -----------------------------------------------------------------------------

.PHONY: makemigration
makemigration:
	@echo "==== Creating New Migration ===="
	@./makemigration.sh

.PHONY: migrate
migrate:
	@echo "==== Applying Migrations ===="
	@./migrate.sh