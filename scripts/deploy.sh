#!/bin/bash
# CryptVault Deployment Script
# Automates Docker build, test, and deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="cryptvault"
VERSION=$(python -c "from cryptvault.__version__ import __version__; print(__version__)" 2>/dev/null || echo "latest")
REGISTRY="${DOCKER_REGISTRY:-}"
ENVIRONMENT="${DEPLOY_ENV:-production}"

# Functions
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

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose is not installed (optional)"
    else
        print_success "Docker Compose is installed"
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    print_success "Docker daemon is running"
    
    echo ""
}

# Build Docker image
build_image() {
    print_header "Building Docker Image"
    
    print_info "Building ${IMAGE_NAME}:${VERSION}..."
    
    if docker build -t "${IMAGE_NAME}:${VERSION}" -t "${IMAGE_NAME}:latest" .; then
        print_success "Image built successfully"
    else
        print_error "Image build failed"
        exit 1
    fi
    
    # Show image size
    IMAGE_SIZE=$(docker images "${IMAGE_NAME}:${VERSION}" --format "{{.Size}}")
    print_info "Image size: ${IMAGE_SIZE}"
    
    echo ""
}

# Test Docker image
test_image() {
    print_header "Testing Docker Image"
    
    # Test 1: Version check
    print_info "Test 1: Version check"
    if docker run --rm "${IMAGE_NAME}:${VERSION}" --version &> /dev/null; then
        print_success "Version check passed"
    else
        print_error "Version check failed"
        exit 1
    fi
    
    # Test 2: Help command
    print_info "Test 2: Help command"
    if docker run --rm "${IMAGE_NAME}:${VERSION}" --help &> /dev/null; then
        print_success "Help command passed"
    else
        print_error "Help command failed"
        exit 1
    fi
    
    # Test 3: Health check
    print_info "Test 3: Health check"
    if docker run --rm "${IMAGE_NAME}:${VERSION}" --status &> /dev/null; then
        print_success "Health check passed"
    else
        print_warning "Health check failed (may require API access)"
    fi
    
    echo ""
}

# Tag image for registry
tag_image() {
    if [ -n "$REGISTRY" ]; then
        print_header "Tagging Image for Registry"
        
        print_info "Tagging ${IMAGE_NAME}:${VERSION} as ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
        docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
        docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:latest"
        
        print_success "Image tagged for registry"
        echo ""
    fi
}

# Push image to registry
push_image() {
    if [ -n "$REGISTRY" ]; then
        print_header "Pushing Image to Registry"
        
        print_info "Pushing ${REGISTRY}/${IMAGE_NAME}:${VERSION}..."
        if docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"; then
            print_success "Version tag pushed"
        else
            print_error "Failed to push version tag"
            exit 1
        fi
        
        print_info "Pushing ${REGISTRY}/${IMAGE_NAME}:latest..."
        if docker push "${REGISTRY}/${IMAGE_NAME}:latest"; then
            print_success "Latest tag pushed"
        else
            print_error "Failed to push latest tag"
            exit 1
        fi
        
        echo ""
    fi
}

# Deploy with Docker Compose
deploy_compose() {
    print_header "Deploying with Docker Compose"
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found"
        exit 1
    fi
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        print_warning ".env file not found, using .env.example"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "Created .env from .env.example"
        fi
    fi
    
    # Pull/build images
    print_info "Preparing services..."
    docker-compose build
    
    # Start services
    print_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 5
    
    # Check service status
    if docker-compose ps | grep -q "Up"; then
        print_success "Services deployed successfully"
        docker-compose ps
    else
        print_error "Service deployment failed"
        docker-compose logs
        exit 1
    fi
    
    echo ""
}

# Create backup
create_backup() {
    print_header "Creating Backup"
    
    BACKUP_DIR="backups"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/cryptvault_backup_${TIMESTAMP}.tar.gz"
    
    mkdir -p "${BACKUP_DIR}"
    
    print_info "Creating backup: ${BACKUP_FILE}"
    
    # Backup logs, data, and configuration
    tar -czf "${BACKUP_FILE}" \
        logs/ \
        data/ \
        .cryptvault_predictions/ \
        config/ \
        .env \
        2>/dev/null || true
    
    if [ -f "${BACKUP_FILE}" ]; then
        BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
        print_success "Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"
    else
        print_warning "Backup creation failed or no data to backup"
    fi
    
    # Keep only last 5 backups
    print_info "Cleaning old backups (keeping last 5)..."
    ls -t "${BACKUP_DIR}"/cryptvault_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    
    echo ""
}

# Health check
health_check() {
    print_header "Health Check"
    
    if docker-compose ps | grep -q "cryptvault"; then
        print_info "Checking service health..."
        
        # Check if container is running
        if docker-compose ps cryptvault | grep -q "Up"; then
            print_success "Service is running"
            
            # Check logs for errors
            if docker-compose logs --tail=50 cryptvault | grep -qi "error"; then
                print_warning "Errors found in logs"
                docker-compose logs --tail=20 cryptvault
            else
                print_success "No errors in recent logs"
            fi
        else
            print_error "Service is not running"
            docker-compose logs --tail=50 cryptvault
            exit 1
        fi
    else
        print_warning "Service not deployed with Docker Compose"
    fi
    
    echo ""
}

# Show deployment info
show_info() {
    print_header "Deployment Information"
    
    echo "Image: ${IMAGE_NAME}:${VERSION}"
    echo "Environment: ${ENVIRONMENT}"
    if [ -n "$REGISTRY" ]; then
        echo "Registry: ${REGISTRY}"
    fi
    echo ""
    
    print_info "Available commands:"
    echo "  docker run --rm ${IMAGE_NAME}:${VERSION} BTC 60 1d"
    echo "  docker-compose up -d"
    echo "  docker-compose logs -f"
    echo "  docker-compose down"
    echo ""
}

# Cleanup
cleanup() {
    print_header "Cleanup"
    
    print_info "Removing dangling images..."
    docker image prune -f
    
    print_info "Removing unused volumes..."
    docker volume prune -f
    
    print_success "Cleanup completed"
    echo ""
}

# Main deployment flow
main() {
    print_header "CryptVault Deployment Script"
    echo "Version: ${VERSION}"
    echo "Environment: ${ENVIRONMENT}"
    echo ""
    
    # Parse arguments
    SKIP_BUILD=false
    SKIP_TEST=false
    SKIP_PUSH=false
    SKIP_DEPLOY=false
    DO_BACKUP=false
    DO_CLEANUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-test)
                SKIP_TEST=true
                shift
                ;;
            --skip-push)
                SKIP_PUSH=true
                shift
                ;;
            --skip-deploy)
                SKIP_DEPLOY=true
                shift
                ;;
            --backup)
                DO_BACKUP=true
                shift
                ;;
            --cleanup)
                DO_CLEANUP=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --skip-build    Skip Docker image build"
                echo "  --skip-test     Skip image testing"
                echo "  --skip-push     Skip pushing to registry"
                echo "  --skip-deploy   Skip deployment"
                echo "  --backup        Create backup before deployment"
                echo "  --cleanup       Cleanup unused Docker resources"
                echo "  --help          Show this help message"
                echo ""
                echo "Environment Variables:"
                echo "  DOCKER_REGISTRY   Docker registry URL"
                echo "  DEPLOY_ENV        Deployment environment (default: production)"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Execute deployment steps
    check_prerequisites
    
    if [ "$DO_BACKUP" = true ]; then
        create_backup
    fi
    
    if [ "$SKIP_BUILD" = false ]; then
        build_image
    fi
    
    if [ "$SKIP_TEST" = false ]; then
        test_image
    fi
    
    if [ "$SKIP_PUSH" = false ]; then
        tag_image
        push_image
    fi
    
    if [ "$SKIP_DEPLOY" = false ]; then
        deploy_compose
        health_check
    fi
    
    if [ "$DO_CLEANUP" = true ]; then
        cleanup
    fi
    
    show_info
    
    print_header "Deployment Complete"
    print_success "CryptVault ${VERSION} deployed successfully!"
}

# Run main function
main "$@"
