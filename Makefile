# =============================================================================
# LLM Calendar Assistant - Local Development (Hybrid Mode)
# =============================================================================
export TZ=UTC
# Load environment variables from .env file
ifeq (,$(wildcard .env))
$(error ".env file not found. Please create it or copy from .env.example")
endif
include .env
export

# Defaults
PROJECT_NAME ?= llm-calendar-assistant
API_PORT ?= 8080
FLOWER_PORT ?= 5555
REDIS_PORT ?= 6379
REDIS_DB ?= 0

REDIS_CONTAINER=${PROJECT_NAME}_redis
FLOWER_CONTAINER=${PROJECT_NAME}_flower
REDIS_VOLUME=${PROJECT_NAME}_redis_data

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

.PHONY: help
help:
	@echo "🔧 Local Dev Commands (Hybrid Mode)"
	@echo "  make redis         - Start Redis (message broker)"
	@echo "  make celery        - Start Celery worker"
	@echo "  make api           - Start FastAPI"
	@echo "  make flower        - Start Flower (waits for Celery workers)"
	@echo "  make status        - Check service status"
	@echo "  make logs          - Show application logs"
	@echo "  make stop          - Stop all services (preserves data)"
	@echo "  make clean         - Stop all services and remove all containers & data"
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
	@echo "🚀 Starting Redis..."
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
	@echo "🌼 Starting Flower..."
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
			mher/flower:2.0 \
			celery --broker=redis://host.docker.internal:$(REDIS_PORT)/$(REDIS_DB) flower --port=5555 --auto_refresh=True > /dev/null; \
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
	@echo "⚙️ Starting Celery worker..."
	@uv run celery -A app.worker.start_worker:app worker

.PHONY: api
api:
	@echo "🚀 Starting FastAPI..."
	@echo "📋 Running migrations..."
	@./migrate.sh
	@echo "🌐 Starting server on localhost:$(API_PORT)..."
	@uv run uvicorn app.main:app --host localhost --port $(API_PORT) --reload

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------

.PHONY: status
status:
	@echo "🔍 Service Status:"
	@printf "  Redis:  " ; docker ps -f "name=$(REDIS_CONTAINER)" --format "{{.Names}}" | grep -q $(REDIS_CONTAINER) && echo "✅" || echo "❌"
	@printf "  Celery: " ; uv run celery -A app.worker.start_worker:app inspect ping > /dev/null 2>&1 && echo "✅" || echo "❌"
	@printf "  API:    " ; curl -s http://localhost:$(API_PORT)/api/v1/health > /dev/null 2>&1 && echo "✅" || echo "❌"
	@printf "  Flower: " ; docker ps -f "name=$(FLOWER_CONTAINER)" --format "{{.Names}}" | grep -q $(FLOWER_CONTAINER) && echo "✅" || echo "❌"

.PHONY: logs
logs:
	@echo "📋 Application logs:"
	@tail -f logs/calendar_assistant.log 2>/dev/null || echo "No logs found. Start services to generate logs."

.PHONY: stop
stop:
	@echo "🛑 Stopping all services..."
	@echo "  • Docker containers"
	@docker stop $(REDIS_CONTAINER) $(FLOWER_CONTAINER) >/dev/null 2>&1 || true
	@echo "  • API processes"
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@echo "  • Worker processes"
	@pkill -f "celery.*app.worker.start_worker" 2>/dev/null || true
	@echo "✅ All services stopped"

.PHONY: clean
clean:
	@echo "🧹 Cleaning everything..."
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
dev:
	@echo "📦 Local Development Setup"
	@make redis
	@echo ""
	@echo "🔥 Next steps - run in separate terminals:"
	@echo "  make celery   # Background worker (start first)"
	@echo "  make api      # FastAPI server"
	@echo "  make flower   # Monitoring (start last)"
	@echo ""
	@echo "💡 Quick check: make status"

# -----------------------------------------------------------------------------
# Database Operations
# -----------------------------------------------------------------------------

.PHONY: makemigration
makemigration:
	@echo "📝 Creating new migration..."
	@./makemigration.sh

.PHONY: migrate
migrate:
	@echo "📋 Applying migrations..."
	@./migrate.sh