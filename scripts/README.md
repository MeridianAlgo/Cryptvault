# CryptVault Deployment Scripts

This directory contains scripts for deploying, managing, and maintaining CryptVault.

## Available Scripts

### Deployment Scripts

#### `deploy.sh` / `deploy.ps1`
Main deployment script that automates the Docker build, test, and deployment process.

**Usage (Linux/macOS)**:
```bash
# Full deployment
./scripts/deploy.sh

# Skip specific steps
./scripts/deploy.sh --skip-build
./scripts/deploy.sh --skip-test
./scripts/deploy.sh --skip-push
./scripts/deploy.sh --skip-deploy

# With backup
./scripts/deploy.sh --backup

# With cleanup
./scripts/deploy.sh --cleanup

# Show help
./scripts/deploy.sh --help
```

**Usage (Windows)**:
```powershell
# Full deployment
.\scripts\deploy.ps1

# Skip specific steps
.\scripts\deploy.ps1 -SkipBuild
.\scripts\deploy.ps1 -SkipTest
.\scripts\deploy.ps1 -SkipPush
.\scripts\deploy.ps1 -SkipDeploy

# With backup
.\scripts\deploy.ps1 -Backup

# With cleanup
.\scripts\deploy.ps1 -Cleanup

# Show help
.\scripts\deploy.ps1 -Help
```

**Environment Variables**:
- `DOCKER_REGISTRY`: Docker registry URL (e.g., `docker.io/username`)
- `DEPLOY_ENV`: Deployment environment (`development`, `testing`, `production`)

**Features**:
- Checks prerequisites (Docker, Docker Compose)
- Builds Docker image with multi-stage optimization
- Runs automated tests on the image
- Tags and pushes to registry (if configured)
- Deploys using Docker Compose
- Performs health checks
- Creates backups (optional)
- Cleans up unused resources (optional)

---

### Backup Scripts

#### `backup.sh` / `backup.ps1`
Creates compressed backups of logs, data, and configuration files.

**Usage (Linux/macOS)**:
```bash
./scripts/backup.sh
```

**Usage (Windows)**:
```powershell
.\scripts\backup.ps1
```

**Features**:
- Backs up logs, data, cache, and configuration
- Creates timestamped backup files
- Automatically removes old backups (keeps last 10)
- Shows backup size and location

**Backup Location**: `backups/cryptvault_backup_YYYYMMDD_HHMMSS.{tar.gz|zip}`

---

### Health Check Scripts

#### `health-check.sh` / `health-check.ps1`
Comprehensive health check for CryptVault deployment.

**Usage (Linux/macOS)**:
```bash
./scripts/health-check.sh
```

**Usage (Windows)**:
```powershell
.\scripts\health-check.ps1
```

**Checks**:
- Docker installation and daemon status
- Image existence and details
- Container status and health
- Docker Compose configuration
- Volume status and sizes
- Configuration files
- Recent logs and errors
- Resource usage (CPU, memory)

**Exit Codes**:
- `0`: All critical checks passed
- `1`: One or more critical checks failed

---

### Development Scripts

#### `run_checks.sh` / `run_checks.bat`
Runs code quality checks (linting, type checking, tests).

**Usage (Linux/macOS)**:
```bash
./scripts/run_checks.sh
```

**Usage (Windows)**:
```cmd
scripts\run_checks.bat
```

#### `setup-git-hooks.sh` / `setup-git-hooks.ps1`
Sets up Git hooks for pre-commit and pre-push checks.

**Usage (Linux/macOS)**:
```bash
./scripts/setup-git-hooks.sh
```

**Usage (Windows)**:
```powershell
.\scripts\setup-git-hooks.ps1
```

---

## Quick Start Guide

### First-Time Deployment

1. **Configure environment**:
   ```bash
   cp .env.example .env
   nano .env  # Edit configuration
   ```

2. **Run deployment**:
   ```bash
   # Linux/macOS
   ./scripts/deploy.sh
   
   # Windows
   .\scripts\deploy.ps1
   ```

3. **Verify deployment**:
   ```bash
   # Linux/macOS
   ./scripts/health-check.sh
   
   # Windows
   .\scripts\health-check.ps1
   ```

### Regular Maintenance

**Create backup before updates**:
```bash
# Linux/macOS
./scripts/backup.sh

# Windows
.\scripts\backup.ps1
```

**Update and redeploy**:
```bash
# Linux/macOS
git pull
./scripts/deploy.sh --backup

# Windows
git pull
.\scripts\deploy.ps1 -Backup
```

**Check system health**:
```bash
# Linux/macOS
./scripts/health-check.sh

# Windows
.\scripts\health-check.ps1
```

---

## Deployment Workflows

### Development Workflow

```bash
# 1. Make changes to code
# 2. Run checks
./scripts/run_checks.sh

# 3. Build and test locally
./scripts/deploy.sh --skip-push --skip-deploy

# 4. Test the image
docker run --rm cryptvault:latest BTC 60 1d
```

### Staging Workflow

```bash
# 1. Set environment
export DEPLOY_ENV=staging
export DOCKER_REGISTRY=registry.example.com

# 2. Deploy to staging
./scripts/deploy.sh --backup

# 3. Run health checks
./scripts/health-check.sh

# 4. Monitor logs
docker-compose logs -f
```

### Production Workflow

```bash
# 1. Create backup
./scripts/backup.sh

# 2. Set environment
export DEPLOY_ENV=production
export DOCKER_REGISTRY=registry.example.com

# 3. Deploy to production
./scripts/deploy.sh --backup

# 4. Verify deployment
./scripts/health-check.sh

# 5. Monitor for issues
docker-compose logs -f cryptvault
```

---

## Troubleshooting

### Script Permission Issues (Linux/macOS)

```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Docker Permission Issues

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Deployment Failures

1. **Check prerequisites**:
   ```bash
   docker --version
   docker-compose --version
   docker info
   ```

2. **View detailed logs**:
   ```bash
   ./scripts/deploy.sh --skip-push --skip-deploy
   docker-compose logs
   ```

3. **Run health check**:
   ```bash
   ./scripts/health-check.sh
   ```

### Backup/Restore Issues

**Restore from backup**:
```bash
# Linux/macOS
tar -xzf backups/cryptvault_backup_YYYYMMDD_HHMMSS.tar.gz

# Windows
Expand-Archive backups\cryptvault_backup_YYYYMMDD_HHMMSS.zip -DestinationPath .
```

---

## Advanced Usage

### Custom Registry Deployment

```bash
# Set registry
export DOCKER_REGISTRY=myregistry.azurecr.io

# Login to registry
docker login myregistry.azurecr.io

# Deploy
./scripts/deploy.sh
```

### Multi-Environment Deployment

```bash
# Development
DEPLOY_ENV=development ./scripts/deploy.sh --skip-push

# Staging
DEPLOY_ENV=staging DOCKER_REGISTRY=registry.example.com ./scripts/deploy.sh

# Production
DEPLOY_ENV=production DOCKER_REGISTRY=registry.example.com ./scripts/deploy.sh --backup
```

### Automated Deployment (CI/CD)

```bash
# In CI/CD pipeline
export DOCKER_REGISTRY=$CI_REGISTRY
export DEPLOY_ENV=production

# Non-interactive deployment
./scripts/deploy.sh --skip-test --cleanup
```

---

## Script Maintenance

### Adding New Scripts

1. Create script in `scripts/` directory
2. Add both `.sh` (Linux/macOS) and `.ps1` (Windows) versions
3. Make shell scripts executable: `chmod +x scripts/your-script.sh`
4. Document in this README
5. Test on both platforms

### Script Naming Convention

- Use kebab-case: `my-script.sh`
- Include platform extension: `.sh` for bash, `.ps1` for PowerShell
- Use descriptive names that indicate purpose

---

## Support

For issues with deployment scripts:
- Check logs: `docker-compose logs`
- Run health check: `./scripts/health-check.sh`
- Review documentation: `docs/DEPLOYMENT.md`
- Open issue: GitHub Issues

