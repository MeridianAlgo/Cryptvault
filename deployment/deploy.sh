#!/bin/bash
# CryptVault - Quick Deploy Script for Unix/Linux/Mac
# Usage: ./deploy.sh [docker|local|pip]

set -e

MODE="${1:-help}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_help() {
    echo ""
    echo -e "${CYAN}CryptVault Deployment Script${NC}"
    echo -e "${CYAN}=============================${NC}"
    echo ""
    echo -e "${YELLOW}Usage: ./deploy.sh [mode]${NC}"
    echo ""
    echo -e "${GREEN}Modes:${NC}"
    echo "  docker    - Build and run with Docker (recommended)"
    echo "  local     - Install locally with virtual environment"
    echo "  pip       - Install as Python package"
    echo "  help      - Show this help message"
    echo ""
}

deploy_docker() {
    echo -e "${CYAN}🐳 Deploying with Docker...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        echo -e "${YELLOW}   Visit: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}📦 Building Docker image...${NC}"
    docker build -t cryptvault:latest .
    
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo ""
    echo -e "${CYAN}Run with:${NC}"
    echo -e "${YELLOW}  docker run --rm cryptvault:latest BTC 60 1d${NC}"
    echo -e "${CYAN}Or use Docker Compose:${NC}"
    echo -e "${YELLOW}  docker-compose run cryptvault BTC 60 1d${NC}"
}

deploy_local() {
    echo -e "${CYAN}🏠 Deploying locally with virtual environment...${NC}"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
    source venv/bin/activate
    
    # Install dependencies
    echo -e "${YELLOW}📥 Installing dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ Local installation complete!${NC}"
    echo ""
    echo -e "${CYAN}Activate the environment with:${NC}"
    echo -e "${YELLOW}  source venv/bin/activate${NC}"
    echo -e "${CYAN}Then run with:${NC}"
    echo -e "${YELLOW}  python cryptvault_cli.py BTC 60 1d${NC}"
}

deploy_pip() {
    echo -e "${CYAN}📦 Installing as Python package...${NC}"
    
    # Install in development mode
    echo -e "${YELLOW}📥 Installing CryptVault...${NC}"
    pip install --upgrade pip
    pip install -e .
    
    echo -e "${GREEN}✅ Package installation complete!${NC}"
    echo ""
    echo -e "${CYAN}Run with:${NC}"
    echo -e "${YELLOW}  cryptvault BTC 60 1d${NC}"
}

# Main execution
case $MODE in
    docker)
        deploy_docker
        ;;
    local)
        deploy_local
        ;;
    pip)
        deploy_pip
        ;;
    help|*)
        show_help
        ;;
esac
