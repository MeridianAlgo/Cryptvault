# Configuration Files

This directory contains all configuration files for development tools, testing, and deployment.

## Files

### Docker & Deployment
- **Dockerfile** - Multi-stage Docker build configuration
- **docker-compose.yml** - Docker Compose orchestration
- **.dockerignore** - Files to exclude from Docker builds

### Code Quality & Linting
- **.pylintrc** - Pylint configuration for code quality checks
- **mypy.ini** - MyPy configuration for type checking
- **.bandit** - Bandit security scanner configuration
- **.pre-commit-config.yaml** - Pre-commit hooks configuration

### Testing
- **pytest.ini** - Pytest configuration and test markers

### Build & Packaging
- **setup.cfg** - Additional setup configuration for setuptools

## Usage

### Docker Commands

```bash
# Build Docker image
docker build -f .config/Dockerfile -t cryptvault:4.0.0 .

# Run with Docker Compose
docker-compose -f .config/docker-compose.yml up -d

# Stop services
docker-compose -f .config/docker-compose.yml down
```

### Testing

```bash
# Run tests (pytest.ini is auto-detected)
pytest

# Or explicitly
pytest -c .config/pytest.ini
```

### Code Quality

```bash
# Run pylint
pylint --rcfile=.config/.pylintrc cryptvault/

# Run mypy
mypy --config-file=.config/mypy.ini cryptvault/

# Run bandit
bandit -c .config/.bandit -r cryptvault/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Note

Most tools will auto-detect these configuration files. If not, use the `-c` or `--config` flag to specify the path.
