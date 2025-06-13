#!/bin/bash

# Docker Compose Logs Script for LLM Calendar Assistant
# Simple log viewing for all services

set -e

# Simple color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Simple output functions
error() { echo -e "${RED}Error:${NC} $1" >&2; exit 1; }
success() { echo -e "${GREEN}✓${NC} $1" || true; }
info() { echo -e "${BLUE}•${NC} $1" || true; }

# Show help
show_help() {
    echo "LLM Calendar Assistant - Docker Logs"
    echo ""
    echo "Usage: $0 [SERVICE] [OPTIONS]"
    echo ""
    echo "Default: Shows last 50 lines from all services"
    echo ""
    echo "Services:"
    echo "  api       FastAPI application logs"
    echo "  celery    Celery worker logs"  
    echo "  redis     Redis logs"
    echo "  flower    Flower monitoring logs"
    echo "  all       All service logs (default)"
    echo ""
    echo "Options:"
    echo "  -f, --follow    Follow in real-time"
    echo "  --tail N        Show last N lines"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      # All logs (last 50 lines)"
    echo "  $0 api -f               # Follow API logs"
    echo "  $0 celery --tail 100    # Last 100 Celery lines"
}

# Parse arguments
parse_args() {
    SERVICE="all"
    FOLLOW=""
    TAIL="50"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            api|celery|redis|flower|all)
                SERVICE="$1"
                shift
                ;;
            -f|--follow)
                FOLLOW="--follow"
                shift
                ;;
            --tail)
                TAIL="$2"
                shift 2
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

# Load project name
load_project_name() {
    if [[ ! -f ".env" ]]; then
        error ".env file not found. Create it from env.sample first."
    fi
    
    PROJECT_NAME=$(grep "^PROJECT_NAME=" .env 2>/dev/null | cut -d'=' -f2 | cut -d'#' -f1 | xargs)
    
    info "Using project: $PROJECT_NAME"
}

# Check if services are running
check_services() {
    local running=$(docker compose -p "${PROJECT_NAME}" ps --services --filter "status=running" 2>/dev/null || true)
    
    if [[ -z "$running" ]]; then
        error "No services are running. Start them with: ./docker/start.sh"
    fi
    
    info "Running services: $(echo $running | tr '\n' ' ')"
}

# Show logs for specific service
show_logs() {
    local compose_cmd="docker compose -p ${PROJECT_NAME}"
    local args="$FOLLOW --tail $TAIL"
    
    case $SERVICE in
        api)
            info "Showing API logs..."
            ${compose_cmd} logs $args api
            ;;
        celery)
            info "Showing Celery logs..."
            ${compose_cmd} logs $args celery
            ;;
        redis)
            info "Showing Redis logs..."
            ${compose_cmd} logs $args redis
            ;;
        flower)
            info "Showing Flower logs..."
            ${compose_cmd} --profile monitoring logs $args flower
            ;;
        all)
            info "Showing all service logs..."
            ${compose_cmd} --profile monitoring logs $args
            ;;
        *)
            error "Unknown service: $SERVICE"
            ;;
    esac
}

# Main execution
main() {
    parse_args "$@"
    
    load_project_name
    check_services
    
    echo ""
    show_logs
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${BLUE}•${NC} Log viewing stopped"; exit 0' INT

# Run main function
main "$@" 