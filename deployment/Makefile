# Makefile for CryptVault - Simplified Build & Deploy
# Works on Windows (with Make installed), Linux, and Mac

.PHONY: help install install-dev test lint format clean docker docker-run docker-compose deploy run

# Default Python command
PYTHON := python
PIP := pip

# Colors for output (works in most terminals)
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help:  ## Show this help message
	@echo "$(CYAN)CryptVault - Makefile Commands$(NC)"
	@echo "================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install:  ## Install dependencies (quick setup)
	@echo "$(CYAN)Installing CryptVault dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Installation complete!$(NC)"

install-dev:  ## Install with development dependencies
	@echo "$(CYAN)Installing with dev dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements/dev.txt
	@echo "$(GREEN)✅ Dev installation complete!$(NC)"

test:  ## Run tests
	@echo "$(CYAN)Running tests...$(NC)"
	pytest tests/ -v --tb=short

test-quick:  ## Run quick tests (skip slow tests)
	@echo "$(CYAN)Running quick tests...$(NC)"
	pytest tests/ -v -m "not slow" --tb=short

lint:  ## Run code quality checks
	@echo "$(CYAN)Running linters...$(NC)"
	black --check cryptvault/ tests/
	flake8 cryptvault/ --max-line-length=100

format:  ## Format code with black
	@echo "$(CYAN)Formatting code...$(NC)"
	black cryptvault/ tests/
	isort cryptvault/ tests/
	@echo "$(GREEN)✅ Code formatted!$(NC)"

clean:  ## Clean build artifacts
	@echo "$(CYAN)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker:  ## Build Docker image
	@echo "$(CYAN)Building Docker image...$(NC)"
	docker build -t cryptvault:latest .
	@echo "$(GREEN)✅ Docker image built!$(NC)"

docker-run:  ## Run CryptVault in Docker (example: make docker-run ARGS="BTC 60 1d")
	@echo "$(CYAN)Running in Docker...$(NC)"
	docker run --rm cryptvault:latest $(ARGS)

docker-compose:  ## Run with Docker Compose
	@echo "$(CYAN)Starting with Docker Compose...$(NC)"
	docker-compose up

deploy-local:  ## Deploy locally (creates venv)
	@echo "$(CYAN)Deploying locally...$(NC)"
	$(PYTHON) -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "$(GREEN)✅ Local deployment complete!$(NC)"
	@echo "$(YELLOW)Activate with: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)$(NC)"

run:  ## Run CryptVault (example: make run ARGS="BTC 60 1d")
	@echo "$(CYAN)Running CryptVault...$(NC)"
	$(PYTHON) cryptvault_cli.py $(ARGS)

demo:  ## Run demo
	@echo "$(CYAN)Running demo...$(NC)"
	$(PYTHON) cryptvault_cli.py --demo

version:  ## Show version
	@$(PYTHON) cryptvault_cli.py --version

all: clean install test  ## Clean, install, and test
