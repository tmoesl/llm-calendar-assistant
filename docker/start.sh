#!/bin/bash

# Docker Compose Startup Script for LLM Calendar Assistant
# Production-ready by default with minimal output

set -e

# Simple color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default settings
QUICK=false
VERBOSE=false
MONITORING=false

# Simple output functions
error() { echo -e "${RED}Error:${NC} $1" >&2; exit 1; }
success() { [[ "$VERBOSE" == true ]] && echo -e "${GREEN}✓${NC} $1" || true; }
info() { [[ "$VERBOSE" == true ]] && echo -e "${BLUE}•${NC} $1" || true; }

# Show help
show_help() {
    echo "LLM Calendar Assistant - Docker Startup"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Default: Starts all services with health checks (production-ready)"
    echo ""
    echo "Options:"
    echo "  --quick       Skip health checks"
    echo "  --monitoring  Enable Flower dashboard"
    echo "  --verbose     Show detailed output"
    echo "  --help        Show this help message"
    echo ""
    echo "Comparison:"
    echo "┌─────────────┬──────────────┬─────────────┬─────────┬───────┐"
    echo "│ Option      │ Health Check │ Services    │ Flower  │ Speed │"
    echo "├─────────────┼──────────────┼─────────────┼─────────┼───────┤"
    echo "│ Default     │ Yes          │ Core        │ No      │ Normal│"
    echo "│ --quick     │ No           │ Core        │ No      │ Fast  │"
    echo "│ --monitoring│ Yes          │ Core        │ Yes     │ Normal│"
    echo "└─────────────┴──────────────┴─────────────┴─────────┴───────┘"
    echo ""
    echo "Examples:"
    echo "  $0                   # Production startup (recommended)"
    echo "  $0 --quick           # Fastest startup"
    echo "  $0 --monitoring      # Include monitoring"
    echo "  $0 --verbose         # Show detailed progress"
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK=true
                shift
                ;;
            --monitoring)
                MONITORING=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1. Use --help for usage information."
                ;;
        esac
    done
}

load_project_name() {
    if [[ ! -f ".env" ]]; then
        error ".env file not found. Create it from env.sample first."
    fi
    
    PROJECT_NAME=$(grep "^PROJECT_NAME=" .env 2>/dev/null | cut -d'=' -f2 | cut -d'#' -f1 | xargs)
    
    info "Using project: $PROJECT_NAME"
}

# Check required files
check_files() {
    [[ ! -f ".env.docker" ]] && error ".env.docker file not found. Create it from env.docker.sample first."
    [[ ! -f "docker-compose.yml" ]] && error "docker-compose.yml not found."
    info "Configuration files ready"
}

# Create directories
setup_directories() {
    mkdir -p logs
    info "Directories ready"
}

# Start services
start_services() {
    local compose_cmd="docker compose -p ${PROJECT_NAME}"
    
    if [[ "$QUICK" == true ]]; then
        echo "🚀 Quick startup..."
        ${compose_cmd} up --build -d
    else
        echo "🚀 Starting services..."
        info "Building and starting Redis..."
        ${compose_cmd} up --build -d redis
        
        # Simple health check for Redis
        info "Waiting for Redis..."
        timeout=10
        while [ $timeout -gt 0 ] && ! ${compose_cmd} exec redis redis-cli ping &>/dev/null; do
            sleep 1
            timeout=$((timeout - 1))
        done
        
        [[ $timeout -le 0 ]] && error "Redis failed to start"
        success "Redis ready"
        
        info "Starting application services..."
        ${compose_cmd} up -d
    fi
    
    # Enable monitoring if requested
    if [[ "$MONITORING" == true ]]; then
        info "Enabling monitoring..."
        ${compose_cmd} --profile monitoring up -d flower
    fi
}

# Show final status
show_status() {
    API_PORT=$(grep "^API_PORT=" .env 2>/dev/null | cut -d'=' -f2 | cut -d'#' -f1 | xargs)
    FLOWER_PORT=$(grep "^FLOWER_PORT=" .env 2>/dev/null | cut -d'=' -f2 | cut -d'#' -f1 | xargs)
    
    echo ""
    echo "✅ Services started successfully!"
    echo ""
    echo "🔗 FastAPI:    http://localhost:${API_PORT}"
    echo "📘 API Docs:   http://localhost:${API_PORT}/docs"
    
    if [[ "$MONITORING" == true ]]; then
        echo "📊 Flower:     http://localhost:${FLOWER_PORT}"
    fi
    
    if [[ "$VERBOSE" == true ]]; then
        echo ""
        info "Management commands:"
        echo "  📋 Logs:  ./docker/logs.sh"
        echo "  🛑 Stop:  ./docker/stop.sh"
    fi
}

# Main execution
main() {
    parse_args "$@"
    
    load_project_name
    check_files
    setup_directories
    start_services
    show_status
}

# Run main function
main "$@" 