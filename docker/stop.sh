#!/bin/bash

# Docker Compose Stop Script for LLM Calendar Assistant
# Clean stop by default with minimal output

set -e

# Simple color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default settings
QUICK=false
VERBOSE=false
CLEANUP=false
ALL=false

# Simple output functions
error() { echo -e "${RED}Error:${NC} $1" >&2; exit 1; }
success() { [[ "$VERBOSE" == true ]] && echo -e "${GREEN}✓${NC} $1" || true; }
info() { [[ "$VERBOSE" == true ]] && echo -e "${BLUE}•${NC} $1" || true; }

# Show help
show_help() {
    echo "LLM Calendar Assistant - Docker Stop"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Default: Clean stop of all services (keeps volumes, images, networks)"
    echo ""
    echo "Options:"
    echo "  --quick     Fast stop without cleanup"
    echo "  --cleanup   Stop + remove networks"
    echo "  --all       Remove everything (nuclear option)"
    echo "  --verbose   Show detailed output"
    echo "  --help      Show this help message"
    echo ""
    echo "Comparison:"
    echo "┌─────────────┬────────────┬──────────┬─────────┬────────┬───────┐"
    echo "│ Option      │ Containers │ Networks │ Volumes │ Images │ Speed │"
    echo "├─────────────┼────────────┼──────────┼─────────┼────────┼───────┤"
    echo "│ Default     │ Remove     │ Keep     │ Keep    │ Keep   │ Normal│"
    echo "│ --quick     │ Remove     │ Keep     │ Keep    │ Keep   │ Fast  │"
    echo "│ --cleanup   │ Remove     │ Remove   │ Keep    │ Keep   │ Normal│"
    echo "│ --all       │ Remove     │ Remove   │ Remove  │ Remove │ Normal│"
    echo "└─────────────┴────────────┴──────────┴─────────┴────────┴───────┘"
    echo ""
    echo "Examples:"
    echo "  $0"               
    echo "  $0 --quick"      
    echo "  $0 --cleanup"    
    echo "  $0 --all"        
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK=true
                shift
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            --all)
                ALL=true
                CLEANUP=true
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

# Load project name
load_project_name() {
    if [[ ! -f ".env" ]]; then
        error ".env file not found. Create it from env.sample first."
    fi
    
    PROJECT_NAME=$(grep "^PROJECT_NAME=" .env 2>/dev/null | cut -d'=' -f2 | cut -d'#' -f1 | xargs)
    
    info "Using project: $PROJECT_NAME"
}

# Stop services
stop_services() {
    local compose_cmd="docker compose -p ${PROJECT_NAME}"
    
    if [[ "$QUICK" == true ]]; then
        echo "🛑 Quick stop..."
        ${compose_cmd} down --remove-orphans
    else
        echo "🛑 Stopping services..."
        info "Stopping all services including monitoring..."
        ${compose_cmd} --profile monitoring down --remove-orphans
        success "All services stopped"
    fi
}

# Cleanup containers and networks
cleanup_resources() {
    if [[ "$CLEANUP" == true ]]; then
        info "Cleaning up containers and networks..."
        docker network prune -f &>/dev/null
        success "Containers and networks cleaned"
        
        if [[ "$ALL" == true ]]; then
            info "Removing volumes and images..."
            
            # Remove volumes with confirmation for --all
            if [[ "$VERBOSE" == true ]]; then
                echo -e "${RED}Warning:${NC} This will remove all data volumes!"
                read -p "Continue? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    info "Volume removal cancelled"
                    return
                fi
            fi
            
            docker compose -p "${PROJECT_NAME}" --profile monitoring down -v &>/dev/null || true
            docker volume prune -f &>/dev/null || true
            docker images --filter=reference="*${PROJECT_NAME}*" -q | xargs -r docker rmi -f &>/dev/null || true
            docker image prune -f &>/dev/null || true
            
            success "Volumes and images removed"
        fi
    fi
}

# Show final status
show_status() {
    if [[ "$VERBOSE" == true ]]; then
        info "Checking remaining resources..."
        
        local containers=$(docker ps --filter "name=${PROJECT_NAME}" --format "{{.Names}}" 2>/dev/null || true)
        local volumes=$(docker volume ls --filter "name=${PROJECT_NAME}" --format "{{.Name}}" 2>/dev/null || true)
        
        if [[ -n "$containers" ]]; then
            echo "  Running containers: $containers"
        else
            echo "  No containers running"
        fi
        
        if [[ -n "$volumes" ]]; then
            echo "  Remaining volumes: $volumes"
        else
            echo "  No volumes remaining"
        fi
    fi
    
    echo ""
    echo "✅ Stop completed!"
    
    if [[ "$VERBOSE" == true ]]; then
        echo ""
        info "To start services again: ./docker/start.sh"
    fi
}

# Main execution
main() {
    parse_args "$@"
    
    load_project_name
    stop_services
    cleanup_resources
    show_status
}

# Run main function
main "$@" 