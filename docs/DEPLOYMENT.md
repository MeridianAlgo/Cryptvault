# CryptVault Deployment Guide

## Overview

This guide covers deploying CryptVault in various environments, from local development to production cloud deployments. CryptVault can be deployed as a command-line tool, containerized application, or cloud service.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Installation](#local-installation)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration](#configuration)
6. [Environment Variables](#environment-variables)
7. [Production Checklist](#production-checklist)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 2 GB
- Storage: 1 GB
- Python: 3.8+

**Recommended**:
- CPU: 4 cores
- RAM: 4 GB
- Storage: 5 GB
- Python: 3.10+

### Software Dependencies

- Python 3.8 or higher
- pip (Python package manager)
- Git (for source installation)
- Docker (for containerized deployment)

---

## Local Installation

### Standard Installation

#### 1. Install from PyPI (Recommended)

```bash
# Install latest stable version
pip install cryptvault

# Verify installation
cryptvault --version
```

#### 2. Install from Source

```bash
# Clone repository
git clone https://github.com/yourusername/cryptvault.git
cd cryptvault

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
python cryptvault_cli.py --version
```

### Configuration

```bash
# Copy example configuration
cp config/.env.example .env

# Edit configuration
# On Windows:
notepad .env
# On macOS/Linux:
nano .env
```

### Basic Usage

```bash
# Analyze a ticker
cryptvault analyze BTC --days 60

# With custom settings
cryptvault analyze ETH --days 30 --interval 4h --sensitivity 0.7
```

---

## Docker Deployment

CryptVault includes production-ready Docker configuration with multi-stage builds, security best practices, and comprehensive orchestration support.

### Quick Start

```bash
# Build the Docker image
docker build -t cryptvault:latest .

# Run analysis
docker run --rm cryptvault:latest BTC 60 1d

# Run with interactive mode
docker run --rm -it cryptvault:latest --interactive

# Run with persistent logs
docker run --rm -v $(pwd)/logs:/app/logs cryptvault:latest BTC 60 1d
```

### Using Pre-built Image

```bash
# Pull latest image (when available)
docker pull cryptvault/cryptvault:latest

# Run analysis
docker run --rm cryptvault/cryptvault:latest BTC 60 1d

# With environment variables
docker run --rm \
  -e CRYPTOCOMPARE_API_KEY=your_key \
  -e LOG_LEVEL=DEBUG \
  cryptvault/cryptvault:latest ETH 30 1d
```

### Building from Source

The included `Dockerfile` uses a multi-stage build for optimal image size and security:

**Features**:
- Multi-stage build (builder + runtime)
- Minimal base image (python:3.11-slim)
- Non-root user execution
- Optimized layer caching
- Health checks included
- ~200MB final image size

```bash
# Build image
docker build -t cryptvault:latest .

# Build with custom tag
docker build -t cryptvault:4.0.0 .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t cryptvault:latest .
```

### Running Containers

#### Basic Analysis

```bash
# Analyze Bitcoin
docker run --rm cryptvault:latest BTC 60 1d

# Analyze Ethereum with 4-hour interval
docker run --rm cryptvault:latest ETH 30 4h

# Show help
docker run --rm cryptvault:latest --help

# Check version
docker run --rm cryptvault:latest --version
```

#### With Persistent Data

```bash
# Create directories for persistent data
mkdir -p logs data .cryptvault_predictions

# Run with volume mounts
docker run --rm \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.cryptvault_predictions:/app/.cryptvault_predictions \
  cryptvault:latest BTC 60 1d
```

#### With Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Run with environment file
docker run --rm \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  cryptvault:latest BTC 60 1d
```

#### Interactive Mode

```bash
# Run interactive shell
docker run --rm -it \
  -v $(pwd)/logs:/app/logs \
  cryptvault:latest --interactive
```

### Docker Compose

CryptVault includes a comprehensive `docker-compose.yml` for orchestration.

#### Configuration

The `docker-compose.yml` includes:
- Main CryptVault service
- Optional Jupyter notebook service
- Volume management
- Network configuration
- Resource limits
- Environment variable support

#### Basic Usage

```bash
# Start services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f cryptvault

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### Running Specific Commands

Edit `docker-compose.yml` to uncomment desired command:

```yaml
services:
  cryptvault:
    # ... other configuration ...
    command: ["BTC", "60", "1d"]                    # Analyze Bitcoin
    # command: ["--interactive"]                     # Interactive mode
    # command: ["--status"]                          # Check API status
    # command: ["--demo"]                            # Run demo
```

Or override command at runtime:

```bash
# Analyze specific ticker
docker-compose run --rm cryptvault BTC 60 1d

# Run demo
docker-compose run --rm cryptvault --demo

# Check status
docker-compose run --rm cryptvault --status

# Interactive mode
docker-compose run --rm cryptvault --interactive
```

#### With Jupyter Notebook

Enable the Jupyter service for interactive analysis:

```bash
# Start with Jupyter profile
docker-compose --profile jupyter up -d

# Access Jupyter at http://localhost:8888
# No password required (configured for development)

# Stop all services
docker-compose --profile jupyter down
```

#### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Start with environment file
docker-compose --env-file .env up -d
```

### Resource Management

#### Resource Limits

The `docker-compose.yml` includes default resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

Adjust based on your needs:

```bash
# For resource-constrained environments
docker run --rm \
  --cpus="1.0" \
  --memory="1g" \
  cryptvault:latest BTC 60 1d

# For high-performance analysis
docker run --rm \
  --cpus="4.0" \
  --memory="4g" \
  cryptvault:latest BTC 365 1d
```

#### Health Checks

The Dockerfile includes health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' cryptvault | jq
```

### Production Deployment

#### Best Practices

1. **Use specific version tags**:
```bash
docker build -t cryptvault:4.0.0 .
docker tag cryptvault:4.0.0 cryptvault:latest
```

2. **Enable logging**:
```bash
docker run --rm \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  cryptvault:latest BTC 60 1d
```

3. **Use secrets for API keys**:
```bash
# Create secret
echo "your_api_key" | docker secret create cryptocompare_key -

# Use in service
docker service create \
  --name cryptvault \
  --secret cryptocompare_key \
  cryptvault:latest
```

4. **Monitor container metrics**:
```bash
# View resource usage
docker stats cryptvault

# Export metrics
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

#### Docker Swarm

Deploy to Docker Swarm:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml cryptvault

# List services
docker stack services cryptvault

# View logs
docker service logs cryptvault_cryptvault

# Remove stack
docker stack rm cryptvault
```

#### Kubernetes

Example Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cryptvault
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cryptvault
  template:
    metadata:
      labels:
        app: cryptvault
    spec:
      containers:
      - name: cryptvault
        image: cryptvault:latest
        resources:
          limits:
            memory: "2Gi"
            cpu: "2000m"
          requests:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: CRYPTVAULT_ENV
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

### Troubleshooting Docker

#### Common Issues

**Issue**: Permission denied on volume mounts
```bash
# Solution: Fix permissions
sudo chown -R 1000:1000 logs/ data/

# Or run with user override
docker run --rm --user $(id -u):$(id -g) cryptvault:latest BTC 60 1d
```

**Issue**: Container exits immediately
```bash
# Solution: Check logs
docker logs cryptvault

# Run with interactive shell for debugging
docker run --rm -it --entrypoint /bin/bash cryptvault:latest
```

**Issue**: Out of memory
```bash
# Solution: Increase memory limit
docker run --rm --memory="4g" cryptvault:latest BTC 365 1d
```

**Issue**: Build fails
```bash
# Solution: Clean build cache
docker builder prune

# Rebuild without cache
docker build --no-cache -t cryptvault:latest .
```

#### Debugging

```bash
# Run shell in container
docker run --rm -it --entrypoint /bin/bash cryptvault:latest

# Check container processes
docker exec cryptvault ps aux

# View container filesystem
docker exec cryptvault ls -la /app

# Copy files from container
docker cp cryptvault:/app/logs/cryptvault.log ./
```

---

## Cloud Deployment

### AWS Deployment

#### AWS Lambda (Serverless)

**1. Create Lambda Function**

```bash
# Install dependencies to package
pip install -r requirements.txt -t package/

# Copy application
cp -r cryptvault package/
cp cryptvault_cli.py package/

# Create deployment package
cd package
zip -r ../cryptvault-lambda.zip .
cd ..
```

**2. Lambda Handler**

Create `lambda_handler.py`:

```python
import json
from cryptvault.core.analyzer import PatternAnalyzer


def lambda_handler(event, context):
    """AWS Lambda handler for CryptVault analysis."""
    try:
        # Parse input
        ticker = event.get('ticker', 'BTC')
        days = event.get('days', 60)
        interval = event.get('interval', '1d')
        
        # Run analysis
        analyzer = PatternAnalyzer()
        result = analyzer.analyze_ticker(ticker, days, interval)
        
        # Return results
        return {
            'statusCode': 200,
            'body': json.dumps(result.to_dict())
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

**3. Deploy to Lambda**

```bash
# Create Lambda function
aws lambda create-function \
  --function-name cryptvault-analyzer \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://cryptvault-lambda.zip \
  --timeout 300 \
  --memory-size 512
```

#### AWS ECS (Containerized)

**1. Push to ECR**

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag cryptvault:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cryptvault:latest

# Push image
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cryptvault:latest
```

**2. Create ECS Task Definition**

```json
{
  "family": "cryptvault",
  "containerDefinitions": [
    {
      "name": "cryptvault",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cryptvault:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "environment": [
        {"name": "CRYPTVAULT_ENV", "value": "production"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cryptvault",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### AWS EC2 (Traditional)

```bash
# Connect to EC2 instance
ssh -i key.pem ec2-user@instance-ip

# Install Python
sudo yum install python3 python3-pip -y

# Clone repository
git clone https://github.com/yourusername/cryptvault.git
cd cryptvault

# Install dependencies
pip3 install -r requirements.txt

# Configure
cp config/.env.example .env
nano .env

# Run analysis
python3 cryptvault_cli.py analyze BTC
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/cryptvault

# Deploy to Cloud Run
gcloud run deploy cryptvault \
  --image gcr.io/PROJECT_ID/cryptvault \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 300
```

#### Compute Engine

```bash
# Create instance
gcloud compute instances create cryptvault-instance \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --machine-type=e2-medium \
  --zone=us-central1-a

# SSH to instance
gcloud compute ssh cryptvault-instance

# Install and configure (same as EC2)
```

### Azure

#### Azure Container Instances

```bash
# Create resource group
az group create --name cryptvault-rg --location eastus

# Create container instance
az container create \
  --resource-group cryptvault-rg \
  --name cryptvault \
  --image cryptvault/cryptvault:latest \
  --cpu 2 \
  --memory 4 \
  --restart-policy Never \
  --environment-variables CRYPTVAULT_ENV=production
```

#### Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name cryptvault-plan \
  --resource-group cryptvault-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group cryptvault-rg \
  --plan cryptvault-plan \
  --name cryptvault-app \
  --runtime "PYTHON|3.11"

# Deploy code
az webapp deployment source config-zip \
  --resource-group cryptvault-rg \
  --name cryptvault-app \
  --src cryptvault.zip
```

---

## Configuration

### Configuration Files

CryptVault uses YAML configuration files:

```
config/
├── settings.yaml              # Base configuration
├── settings.development.yaml  # Development overrides
├── settings.testing.yaml      # Testing overrides
├── settings.production.yaml   # Production overrides
├── logging.yaml              # Logging configuration
└── .env.example              # Environment variables template
```

### Base Configuration

`config/settings.yaml`:

```yaml
analysis:
  min_data_points: 30
  max_data_points: 1000
  default_interval: "1d"
  default_days: 60

patterns:
  enabled_geometric: true
  enabled_reversal: true
  enabled_harmonic: true
  enabled_candlestick: true
  enabled_divergence: true

sensitivity:
  level: "medium"  # low, medium, high
  geometric_patterns: 0.5
  reversal_patterns: 0.6
  harmonic_patterns: 0.7

display:
  chart_width: 120
  chart_height: 30
  enable_colors: true

data_sources:
  primary: "yfinance"
  fallback: ["ccxt"]
  yfinance_enabled: true
  ccxt_enabled: true
  cache_ttl: 300  # 5 minutes

ml:
  enabled: true
  model_type: "ensemble"
  prediction_horizon: 7
  min_training_samples: 30
```

### Environment-Specific Configuration

`config/settings.production.yaml`:

```yaml
analysis:
  max_data_points: 5000

display:
  enable_colors: false  # Disable for logs

data_sources:
  cache_ttl: 600  # 10 minutes in production

logging:
  level: "WARNING"
  file_enabled: true
  console_enabled: false
```

---

## Environment Variables

### Required Variables

```bash
# Environment
CRYPTVAULT_ENV=production  # development, testing, production

# Logging
CRYPTVAULT_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
CRYPTVAULT_LOG_FILE=logs/cryptvault.log
```

### Optional Variables

```bash
# API Keys (if using premium data sources)
CRYPTOCOMPARE_API_KEY=your_key_here
ALPHAVANTAGE_API_KEY=your_key_here

# Data Source Configuration
CRYPTVAULT_PRIMARY_SOURCE=yfinance
CRYPTVAULT_CACHE_TTL=300

# ML Configuration
CRYPTVAULT_ML_ENABLED=true
CRYPTVAULT_ML_MODEL=ensemble

# Display Configuration
CRYPTVAULT_ENABLE_COLORS=true
CRYPTVAULT_CHART_WIDTH=120
CRYPTVAULT_CHART_HEIGHT=30
```

### Setting Environment Variables

**Linux/macOS**:
```bash
export CRYPTVAULT_ENV=production
export CRYPTVAULT_LOG_LEVEL=INFO
```

**Windows**:
```cmd
set CRYPTVAULT_ENV=production
set CRYPTVAULT_LOG_LEVEL=INFO
```

**Docker**:
```bash
docker run -e CRYPTVAULT_ENV=production cryptvault:latest
```

**Docker Compose**:
```yaml
environment:
  - CRYPTVAULT_ENV=production
  - CRYPTVAULT_LOG_LEVEL=INFO
```

---

## Production Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Configuration validated
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Backup strategy in place

### Configuration

- [ ] Environment set to `production`
- [ ] Logging configured appropriately
- [ ] API keys secured (not in code)
- [ ] Resource limits set
- [ ] Caching enabled
- [ ] Error tracking configured

### Security

- [ ] API keys in environment variables
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (if web service)
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Dependencies updated

### Monitoring

- [ ] Logging configured
- [ ] Metrics collection enabled
- [ ] Alerts configured
- [ ] Health checks implemented
- [ ] Error tracking active

### Performance

- [ ] Caching enabled
- [ ] Resource limits appropriate
- [ ] Database connections pooled (if applicable)
- [ ] Timeouts configured
- [ ] Load testing completed

### Backup and Recovery

- [ ] Backup strategy documented
- [ ] Recovery procedures tested
- [ ] Data retention policy defined
- [ ] Disaster recovery plan in place

---

## Monitoring and Logging

### Logging Configuration

`config/logging.yaml`:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: logs/cryptvault.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  cryptvault:
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: WARNING
  handlers: [console, file]
```

### Metrics to Monitor

**Application Metrics**:
- Analysis success rate
- Average analysis time
- Pattern detection count
- ML prediction accuracy
- Error rate by type

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- API call rate

**Business Metrics**:
- Daily active users
- Analysis requests per day
- Most analyzed tickers
- Feature usage statistics

### Health Checks

Implement health check endpoint:

```python
def health_check():
    """Check system health."""
    checks = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'data_sources': check_data_sources(),
            'ml_models': check_ml_models(),
            'cache': check_cache(),
            'config': check_config()
        }
    }
    return checks
```

---

## Troubleshooting

### Common Issues

**Issue**: Import errors after deployment
```bash
# Solution: Verify all dependencies installed
pip install -r requirements.txt
pip list | grep cryptvault
```

**Issue**: Configuration not loading
```bash
# Solution: Check config file path and permissions
ls -la config/
cat config/settings.yaml
```

**Issue**: API rate limiting
```bash
# Solution: Enable caching and reduce request frequency
# In config/settings.yaml:
data_sources:
  cache_ttl: 600  # Increase cache time
```

**Issue**: Out of memory errors
```bash
# Solution: Reduce max_data_points or increase memory
# In config/settings.yaml:
analysis:
  max_data_points: 500  # Reduce from 1000
```

### Debug Mode

Enable debug logging:

```bash
export CRYPTVAULT_LOG_LEVEL=DEBUG
python cryptvault_cli.py analyze BTC --days 60
```

### Getting Help

- Check logs: `logs/cryptvault.log`
- Review documentation: `docs/`
- Search issues: GitHub Issues
- Contact support: support@cryptvault.io

---

## Maintenance

### Updates

```bash
# Update from PyPI
pip install --upgrade cryptvault

# Update from source
git pull origin main
pip install -r requirements.txt
```

### Backup

```bash
# Backup configuration
tar -czf config-backup.tar.gz config/

# Backup logs
tar -czf logs-backup.tar.gz logs/
```

### Cleanup

```bash
# Clean old logs
find logs/ -name "*.log.*" -mtime +30 -delete

# Clean cache
rm -rf .cache/
```

---

## Support

For deployment assistance:
- Documentation: https://cryptvault.readthedocs.io
- GitHub Issues: https://github.com/yourusername/cryptvault/issues
- Email: support@cryptvault.io
