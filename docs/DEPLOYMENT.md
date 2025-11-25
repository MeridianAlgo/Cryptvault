# Deployment Guide - CryptVault

## Overview

This guide covers deploying CryptVault in various environments, from local development to production.

---

## 🎯 Deployment Methods Comparison

| Method | Setup Time | Best For | Pros | Cons |
|--------|-----------|----------|------|------|
| **Docker** | 2 min | Production, Consistency | Isolated, reproducible | Requires Docker |
| **Local venv** | 3 min | Development, Testing | Full control, easy debugging | Manual setup |
| **Pip install** | 1 min | Quick testing | Fastest setup | No isolation |
| **Make** | 1 min | Automation | Simple commands | Requires Make |

---

## 1. Docker Deployment (Recommended for Production)

### Quick Start
```bash
# Build and run in one command
docker build -t cryptvault:latest . && docker run --rm cryptvault:latest BTC 60 1d
```

### Production Deployment

**Step 1: Build the image**
```bash
docker build -t cryptvault:prod -f Dockerfile .
```

**Step 2: Run as a service**
```bash
docker run -d \
  --name cryptvault \
  --restart unless-stopped \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/.cryptvault_predictions \
  cryptvault:prod
```

**Step 3: View logs**
```bash
docker logs cryptvault
```

**Step 4: Run analysis**
```bash
docker exec cryptvault python cryptvault_cli.py BTC 60 1d
```

### Docker Compose (Multi-Service)

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  cryptvault:
    build: .
    image: cryptvault:latest
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - ./data:/app/.cryptvault_predictions
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    networks:
      - cryptvault-net

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - cryptvault-net

networks:
  cryptvault-net:

volumes:
  redis-data:
```

**Deploy:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 2. Cloud Deployments

### AWS ECS (Elastic Container Service)

**Prerequisites:**
- AWS CLI configured
- ECR repository created

**Steps:**

1. **Build and tag image:**
```bash
docker build -t cryptvault:latest .
docker tag cryptvault:latest <account-id>.dkr.ecr.<region>.amazonaws.com/cryptvault:latest
```

2. **Push to ECR:**
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/cryptvault:latest
```

3. **Create task definition** (`ecs-task-definition.json`):
```json
{
  "family": "cryptvault",
  "containerDefinitions": [
    {
      "name": "cryptvault",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/cryptvault:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cryptvault",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512"
}
```

4. **Deploy:**
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
aws ecs create-service --cluster <cluster-name> --service-name cryptvault --task-definition cryptvault --desired-count 1 --launch-type FARGATE
```

### Google Cloud Run

**Steps:**

1. **Build image:**
```bash
docker build -t gcr.io/<project-id>/cryptvault:latest .
```

2. **Push to GCR:**
```bash
docker push gcr.io/<project-id>/cryptvault:latest
```

3. **Deploy:**
```bash
gcloud run deploy cryptvault \
  --image gcr.io/<project-id>/cryptvault:latest \
  --platform managed \
  --region us-central1 \
  --memory 512Mi
```

### Azure Container Instances

**Steps:**

1. **Create ACR:**
```bash
az acr create --resource-group <rg> --name <acr-name> --sku Basic
```

2. **Build and push:**
```bash
az acr build --registry <acr-name> --image cryptvault:latest .
```

3. **Deploy:**
```bash
az container create \
  --resource-group <rg> \
  --name cryptvault \
  --image <acr-name>.azurecr.io/cryptvault:latest \
  --cpu 1 \
  --memory 1
```

### Heroku

**Create `heroku.yml`:**
```yaml
build:
  docker:
    web: Dockerfile
```

**Deploy:**
```bash
heroku create cryptvault-app
heroku stack:set container
git push heroku main
```

---

## 3. Kubernetes Deployment

### Basic Deployment

**Create `k8s-deployment.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cryptvault
spec:
  replicas: 2
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
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        persistentVolumeClaim:
          claimName: cryptvault-logs
---
apiVersion: v1
kind: Service
metadata:
  name: cryptvault-service
spec:
  selector:
    app: cryptvault
  ports:
  - port: 80
    targetPort: 8000
```

**Deploy:**
```bash
kubectl apply -f k8s-deployment.yaml
```

---

## 4. Local Development

### Using Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python cryptvault_cli.py BTC 60 1d
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python cryptvault_cli.py BTC 60 1d
```

### Using Conda

```bash
conda create -n cryptvault python=3.11
conda activate cryptvault
pip install -r requirements.txt
python cryptvault_cli.py BTC 60 1d
```

---

## 5. CI/CD Integration

### GitHub Actions (Automated)

The project includes `.github/workflows/simplified-ci.yml` which automatically:

1. ✅ Runs quick validation on every push
2. ✅ Runs full tests on pull requests
3. ✅ Builds Docker images on main branch
4. ✅ Performs security scans weekly

**Manual trigger:**
```bash
gh workflow run simplified-ci.yml
```

### GitLab CI

Create `.gitlab-ci.yml`:
```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest
    - pytest tests/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t cryptvault:latest .
    - docker tag cryptvault:latest $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
```

### Jenkins

Create `Jenkinsfile`:
```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest tests/'
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker build -t cryptvault:latest .'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker push cryptvault:latest'
            }
        }
    }
}
```

---

## 6. Environment Configuration

### Environment Variables

Create `.env`:
```bash
# API Keys (optional)
CRYPTOCOMPARE_API_KEY=your_key
ALPHAVANTAGE_API_KEY=your_key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_DIR=.cryptvault_predictions

# Performance
MAX_WORKERS=4
TIMEOUT=30
```

### Configuration Files

**Production config** (`config/production.yaml`):
```yaml
data:
  cache_enabled: true
  cache_ttl: 3600
  
logging:
  level: INFO
  format: json
  
ml:
  models:
    - xgboost
    - lightgbm
    - random_forest
  
performance:
  max_workers: 4
  timeout: 30
```

---

## 7. Monitoring & Logging

### Docker Logging

```bash
# View logs
docker logs cryptvault

# Follow logs
docker logs -f cryptvault

# Export logs
docker logs cryptvault > cryptvault.log
```

### Production Logging

**Using ELK Stack:**
```yaml
# docker-compose.yml with logging
version: '3.8'
services:
  cryptvault:
    image: cryptvault:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 8. Security Best Practices

### Docker Security

1. **Use non-root user:**
```dockerfile
RUN useradd -m -u 1000 cryptvault
USER cryptvault
```

2. **Scan for vulnerabilities:**
```bash
docker scan cryptvault:latest
```

3. **Use secrets management:**
```bash
docker secret create api_key api_key.txt
```

### API Key Management

**Never commit API keys!**

Use environment variables or secret management:
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id cryptvault/api-keys

# Azure Key Vault
az keyvault secret show --vault-name cryptvault --name api-key
```

---

## 9. Performance Tuning

### Docker Optimization

**Multi-stage builds** (already implemented):
- Reduces image size by 60%
- Separates build and runtime dependencies

**Resource limits:**
```bash
docker run --memory="512m" --cpus="1.0" cryptvault:latest
```

### Python Optimization

```python
# Use batch processing for multiple analyses
# Enable caching
# Optimize ML model parameters
```

---

## 10. Troubleshooting

### Common Issues

**Docker build fails:**
```bash
# Clear cache and rebuild
docker system prune -a
docker build --no-cache -t cryptvault .
```

**Permission errors:**
```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Import errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Build Docker | `docker build -t cryptvault .` |
| Run analysis | `docker run --rm cryptvault BTC 60 1d` |
| Deploy local | `./deploy.sh local` |
| Run tests | `make test` |
| View help | `make help` |

---

**For more deployment options, see:**
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [README.md](README.md) - Main documentation
- [.github/workflows/](.github/workflows/) - CI/CD examples
