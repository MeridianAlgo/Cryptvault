# CryptVault - Getting Started in 60 Seconds

Welcome to CryptVault! This guide will get you up and running in under a minute.

## ⚡ Super Quick Start

### For the Impatient (30 seconds)

**Got Docker?**
```bash
docker build -t cryptvault . && docker run --rm cryptvault BTC 60 1d
```
Done! ✅

**No Docker? Use Make:**
```bash
make install && make demo
```
Done! ✅

**Want it even simpler?**
```bash
pip install -r requirements.txt && python cryptvault_cli.py --demo
```
Done! ✅

---

## 📋 Step-by-Step (60 seconds)

### Step 1: Choose Your Method (5 seconds)

Pick ONE of these:
- 🐳 **Docker** - Best for everyone (especially beginners)
- 🛠️ **Make** - Best if you have Make installed
- 🐍 **Python** - Best if you're familiar with Python

### Step 2: Run Commands (30 seconds)

**Method A: Docker**
```bash
# Clone (if you haven't)
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Build & Run
docker build -t cryptvault .
docker run --rm cryptvault --demo
```

**Method B: Make**
```bash
# Clone (if you haven't)
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Install & Run
make install
make demo
```

**Method C: Python**
```bash
# Clone (if you haven't)
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Install & Run
pip install -r requirements.txt
python cryptvault_cli.py --demo
```

### Step 3: Analyze Your First Asset (10 seconds)

```bash
# Using Docker
docker run --rm cryptvault BTC 60 1d

# Using Make
make run ARGS="BTC 60 1d"

# Using Python
python cryptvault_cli.py BTC 60 1d
```

### Step 4: See the Results! (15 seconds)

You should see:
- ✅ Pattern detection results
- ✅ Technical indicators
- ✅ Price predictions
- ✅ Interactive chart (if GUI available)

---

## 🎯 What Just Happened?

You analyzed Bitcoin (BTC) with:
- **60 days** of historical data
- **1 day** interval candles
- **50+ chart patterns** detected
- **40+ technical indicators** calculated
- **ML predictions** generated

---

## 🚀 Next Steps

### Try Different Assets

**Cryptocurrencies:**
```bash
python cryptvault_cli.py ETH 60 1d      # Ethereum
python cryptvault_cli.py SOL 90 1d      # Solana
python cryptvault_cli.py ADA 60 1d      # Cardano
```

**Stocks:**
```bash
python cryptvault_cli.py AAPL 60 1d     # Apple
python cryptvault_cli.py TSLA 90 1d     # Tesla
python cryptvault_cli.py GOOGL 60 1d    # Google
```

### Advanced Features

**Portfolio Analysis:**
```bash
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10
```

**Compare Multiple Assets:**
```bash
python cryptvault_cli.py --compare BTC ETH SOL
```

**Interactive Mode:**
```bash
python cryptvault_cli.py --interactive
```

**Save Charts:**
```bash
python cryptvault_cli.py BTC 60 1d --save-chart btc_analysis.png
```

---

## 📖 Learn More

- **Quick Features**: See [README.md](README.md)
- **All Deployment Options**: See [QUICKSTART.md](QUICKSTART.md)
- **Production Setup**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 💡 Pro Tips

### Use Make for Everything
```bash
make help          # See all commands
make install       # Install dependencies
make run           # Run analysis
make test          # Run tests
make docker        # Build Docker image
```

### Use Docker Compose for Services
```bash
docker-compose run cryptvault BTC 60 1d
docker-compose run cryptvault --demo
```

### Use Deployment Scripts
```bash
# Windows
.\deploy.ps1 docker

# Linux/Mac
./deploy.sh docker
```

---

## 🆘 Troubleshooting

### Command not found?
```bash
# Make sure you're in the right directory
cd Cryptvault
ls  # Should see cryptvault_cli.py
```

### Import errors?
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Docker errors?
```bash
# Make sure Docker is running
docker --version

# Rebuild without cache
docker build --no-cache -t cryptvault .
```

### Permission denied?
```bash
# Linux/Mac
chmod +x deploy.sh
chmod +x cryptvault_cli.py

# Windows (PowerShell as Admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## ✅ Quick Reference Card

| Task | Command |
|------|---------|
| Install | `make install` |
| Demo | `make demo` |
| Analyze BTC | `make run ARGS="BTC 60 1d"` |
| Run Tests | `make test` |
| Build Docker | `make docker` |
| Show Help | `make help` |

| Docker Task | Command |
|-------------|---------|
| Build | `docker build -t cryptvault .` |
| Run Demo | `docker run --rm cryptvault --demo` |
| Analyze | `docker run --rm cryptvault BTC 60 1d` |
| Compose | `docker-compose run cryptvault BTC 60 1d` |

---

## 🎉 You're Ready!

That's it! You're now ready to use CryptVault for cryptocurrency and stock analysis.

**Happy analyzing! 📊📈**

---

**Questions?** Open an issue at: https://github.com/MeridianAlgo/Cryptvault/issues
