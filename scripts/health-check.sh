#!/bin/bash
# CryptVault Health Check Script
# Checks the health of CryptVault deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONTAINER_NAME="${CONTAINER_NAME:-cryptvault}"
IMAGE_NAME="${IMAGE_NAME:-cryptvault:latest}"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check Docker
check_docker() {
    print_header "Docker Status"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi
    print_success "Docker is installed"
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        return 1
    fi
    print_success "Docker daemon is running"
    
    echo ""
}

# Check image
check_image() {
    print_header "Image Status"
    
    if docker images "${IMAGE_NAME}" --format "{{.Repository}}:{{.Tag}}" | grep -q "${IMAGE_NAME}"; then
        print_success "Image ${IMAGE_NAME} exists"
        
        IMAGE_SIZE=$(docker images "${IMAGE_NAME}" --format "{{.Size}}")
        IMAGE_CREATED=$(docker images "${IMAGE_NAME}" --format "{{.CreatedSince}}")
        print_info "Size: ${IMAGE_SIZE}"
        print_info "Created: ${IMAGE_CREATED}"
    else
        print_warning "Image ${IMAGE_NAME} not found"
    fi
    
    echo ""
}

# Check container
check_container() {
    print_header "Container Status"
    
    if docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "${CONTAINER_NAME}"; then
        print_success "Container ${CONTAINER_NAME} exists"
        
        # Check if running
        if docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "${CONTAINER_NAME}"; then
            print_success "Container is running"
            
            # Get container stats
            CONTAINER_STATUS=$(docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Status}}")
            print_info "Status: ${CONTAINER_STATUS}"
            
            # Check health
            HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "${CONTAINER_NAME}" 2>/dev/null || echo "none")
            if [ "$HEALTH" = "healthy" ]; then
                print_success "Health check: healthy"
            elif [ "$HEALTH" = "none" ]; then
                print_info "Health check: not configured"
            else
                print_warning "Health check: ${HEALTH}"
            fi
        else
            print_warning "Container is not running"
            CONTAINER_STATUS=$(docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Status}}")
            print_info "Status: ${CONTAINER_STATUS}"
        fi
    else
        print_warning "Container ${CONTAINER_NAME} not found"
    fi
    
    echo ""
}

# Check Docker Compose
check_compose() {
    print_header "Docker Compose Status"
    
    if [ -f "docker-compose.yml" ]; then
        print_success "docker-compose.yml exists"
        
        if command -v docker-compose &> /dev/null; then
            print_success "Docker Compose is installed"
            
            # Check services
            if docker-compose ps | grep -q "cryptvault"; then
                print_success "Services are defined"
                
                # Show service status
                echo ""
                print_info "Service status:"
                docker-compose ps
            else
                print_warning "No services running"
            fi
        else
            print_warning "Docker Compose is not installed"
        fi
    else
        print_warning "docker-compose.yml not found"
    fi
    
    echo ""
}

# Check logs
check_logs() {
    print_header "Recent Logs"
    
    if docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "${CONTAINER_NAME}"; then
        print_info "Last 10 log entries:"
        echo ""
        docker logs --tail=10 "${CONTAINER_NAME}" 2>&1
        
        # Check for errors
        ERROR_COUNT=$(docker logs --tail=100 "${CONTAINER_NAME}" 2>&1 | grep -ci "error" || true)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            print_warning "Found ${ERROR_COUNT} error(s) in recent logs"
        else
            print_success "No errors in recent logs"
        fi
    else
        print_warning "Container not running, cannot check logs"
    fi
    
    echo ""
}

# Check resources
check_resources() {
    print_header "Resource Usage"
    
    if docker ps --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "${CONTAINER_NAME}"; then
        print_info "Container resource usage:"
        echo ""
        docker stats --no-stream "${CONTAINER_NAME}"
    else
        print_warning "Container not running, cannot check resources"
    fi
    
    echo ""
}

# Check volumes
check_volumes() {
    print_header "Volume Status"
    
    if [ -d "logs" ]; then
        LOG_SIZE=$(du -sh logs 2>/dev/null | cut -f1)
        print_success "Logs directory exists (${LOG_SIZE})"
    else
        print_warning "Logs directory not found"
    fi
    
    if [ -d "data" ]; then
        DATA_SIZE=$(du -sh data 2>/dev/null | cut -f1)
        print_success "Data directory exists (${DATA_SIZE})"
    else
        print_warning "Data directory not found"
    fi
    
    if [ -d ".cryptvault_predictions" ]; then
        CACHE_SIZE=$(du -sh .cryptvault_predictions 2>/dev/null | cut -f1)
        print_success "Cache directory exists (${CACHE_SIZE})"
    else
        print_warning "Cache directory not found"
    fi
    
    echo ""
}

# Check configuration
check_config() {
    print_header "Configuration Status"
    
    if [ -f ".env" ]; then
        print_success ".env file exists"
    else
        print_warning ".env file not found"
        if [ -f ".env.example" ]; then
            print_info "Use: cp .env.example .env"
        fi
    fi
    
    if [ -d "config" ]; then
        print_success "Config directory exists"
        CONFIG_FILES=$(ls -1 config/*.yaml 2>/dev/null | wc -l)
        print_info "Found ${CONFIG_FILES} configuration file(s)"
    else
        print_warning "Config directory not found"
    fi
    
    echo ""
}

# Main health check
main() {
    print_header "CryptVault Health Check"
    echo ""
    
    EXIT_CODE=0
    
    check_docker || EXIT_CODE=1
    check_image
    check_container
    check_compose
    check_volumes
    check_config
    check_logs
    check_resources
    
    print_header "Health Check Summary"
    
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "All critical checks passed"
    else
        print_error "Some critical checks failed"
    fi
    
    exit $EXIT_CODE
}

# Run main function
main
