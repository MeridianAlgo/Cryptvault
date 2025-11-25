# CryptVault - Quick Start Guide

## 🚀 30-Second Quick Start

### Option 1: Docker (Recommended - No Setup Required!)
```bash
# Build and run in one command
docker build -t cryptvault . && docker run --rm cryptvault BTC 60 1d

# Or with Docker Compose
docker-compose run cryptvault BTC 60 1d
```

### Option 2: Local Install (Traditional)
```bash
# Install dependencies
pip install -r requirements.txt

# Run analysis
python cryptvault_cli.py BTC 60 1d
```

### Option 3: Use Makefile (Easiest)
```bash
# Install
make install

# Run
make run ARGS="BTC 60 1d"

# Or run demo
make demo
```

---

## 📦 Detailed Deployment Options

### 1. Docker Deployment (Production-Ready)

**Build the image:**
```bash
docker build -t cryptvault:latest .
```

**Run analysis:**
```bash
# Cryptocurrency analysis
docker run --rm cryptvault BTC 60 1d
docker run --rm cryptvault ETH 90 1d

# Stock analysis
docker run --rm cryptvault AAPL 60 1d

# With volume mounting for persistence
docker run --rm -v $(pwd)/logs:/app/logs cryptvault BTC 60 1d
```

**Using Docker Compose:**
```bash
# Run with compose
docker-compose run cryptvault BTC 60 1d

# Interactive mode
docker-compose run cryptvault --interactive
```

---

### 2. Local Installation

**Windows:**
```powershell
# Use the deployment script
.\deploy.ps1 local

# Or manually
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python cryptvault_cli.py BTC 60 1d
```

**Linux/Mac:**
```bash
# Use the deployment script
chmod +x deploy.sh
./deploy.sh local

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python cryptvault_cli.py BTC 60 1d
```

---

### 3. Package Installation

**Install as Python package:**
```bash
pip install -e .
cryptvault BTC 60 1d
```

---

## 🔧 Using the Deployment Scripts

### Automated Deployment (Recommended)

**Windows:**
```powershell
# Show help
.\deploy.ps1 help

# Deploy with Docker
.\deploy.ps1 docker

# Deploy locally
.\deploy.ps1 local

# Install as package
.\deploy.ps1 pip
```

**Linux/Mac:**
```bash
chmod +x deploy.sh

# Show help
./deploy.sh help

# Deploy with Docker
./deploy.sh docker

# Deploy locally
./deploy.sh local

# Install as package
./deploy.sh pip
```

---

## 🛠 Using Make Commands

```bash
# Show all available commands
make help

# Install dependencies
make install

# Install with dev dependencies
make install-dev

# Run analysis
make run ARGS="BTC 60 1d"

# Run demo
make demo

# Build Docker image
make docker

# Run in Docker
make docker-run ARGS="BTC 60 1d"

# Run tests
make test

# Format code
make format

# Clean build artifacts
make clean
```

---

## 📊 Example Commands

### Basic Analysis
```bash
# Cryptocurrency
python cryptvault_cli.py BTC 60 1d
python cryptvault_cli.py ETH 90 1d --save-chart eth.png

# Stocks
python cryptvault_cli.py AAPL 60 1d
python cryptvault_cli.py TSLA 90 1d --verbose
```

### Advanced Features
```bash
# Portfolio analysis
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10

# Compare multiple assets
python cryptvault_cli.py --compare BTC ETH SOL

# Interactive mode
python cryptvault_cli.py --interactive

# Demo mode
python cryptvault_cli.py --demo
```

---

## 🐳 Production Deployment

### Docker in Production

**1. Build optimized image:**
```bash
docker build -t cryptvault:prod .
```

**2. Run as service:**
```bash
docker run -d \
  --name cryptvault-service \
  --restart unless-stopped \
  -v /path/to/logs:/app/logs \
  cryptvault:prod
```

**3. With Docker Compose (Recommended):**
```yaml
# Create docker-compose.prod.yml
version: '3.8'
services:
  cryptvault:
    image: cryptvault:latest
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
      - ./data:/app/.cryptvault_predictions
    environment:
      - PYTHONUNBUFFERED=1
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 CI/CD Integration

### GitHub Actions

The project includes simplified CI/CD workflows:

- **Quick Check**: Runs on every push (fast validation)
- **Full Tests**: Runs on PRs (comprehensive testing)
- **Docker Build**: Runs on main branch (production ready)
- **Security Scan**: Runs weekly (dependency scanning)

**Workflow file:** `.github/workflows/simplified-ci.yml`

### Manual Trigger
```bash
# Trigger workflow manually
gh workflow run simplified-ci.yml
```

---

## 🧪 Development Setup

```bash
# Clone repository
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Install with dev dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linters
make lint
```

---

## 📝 Environment Variables

Create a `.env` file (optional):
```bash
# API Keys (if using premium data sources)
# CRYPTOCOMPARE_API_KEY=your_key_here
# ALPHAVANTAGE_API_KEY=your_key_here

# Logging
LOG_LEVEL=INFO

# Cache settings
CACHE_ENABLED=true
CACHE_TTL=3600
```

---

## 🆘 Troubleshooting

### Common Issues

**1. Import errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**2. Docker build fails:**
```bash
# Clean Docker cache
docker system prune -a
docker build --no-cache -t cryptvault .
```

**3. Permission denied on scripts:**
```bash
# Linux/Mac
chmod +x deploy.sh

# Windows: Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**4. Module not found:**
```bash
# Ensure you're in the correct directory
cd Cryptvault

# Reinstall
pip install -r requirements.txt
```

---

## 🎯 Quick Reference

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make run ARGS="BTC 60 1d"` | Run analysis |
| `make docker` | Build Docker image |
| `make test` | Run tests |
| `make help` | Show all commands |

| Docker Command | Description |
|----------------|-------------|
| `docker build -t cryptvault .` | Build image |
| `docker run --rm cryptvault BTC 60 1d` | Run analysis |
| `docker-compose run cryptvault --demo` | Run demo |

---

## 📚 Next Steps

1. ✅ Choose your deployment method
2. ✅ Run the demo: `python cryptvault_cli.py --demo`
3. ✅ Analyze your first asset: `python cryptvault_cli.py BTC 60 1d`
4. ✅ Explore advanced features in the main [README.md](README.md)

---

**Need help?** Check the main [README.md](README.md) or open an issue on GitHub!
