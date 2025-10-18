# CryptVault Quick Guide

## What's the Difference?

### cryptvault_cli.py (Recommended) 🌟
**The full-featured application with everything you need**

```bash
python cryptvault_cli.py BTC 60 1d
```

**Features:**
- ✅ Complete analysis with ML predictions
- ✅ Portfolio management
- ✅ Multi-asset comparison
- ✅ Interactive mode
- ✅ Desktop charts
- ✅ Prediction tracking
- ✅ Demo mode
- ✅ Status checks

**Use this for:** Daily trading, portfolio management, full analysis

---

### cryptvault.py
**Lightweight terminal charts for quick visualization**

```bash
python cryptvault.py BTC 60 1d
```

**Features:**
- ✅ Terminal ASCII charts
- ✅ Pattern detection
- ✅ Basic ML predictions
- ✅ Fast execution

**Use this for:** Quick charts, scripting, automation

---

## Quick Start

### 1. Install
```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
```

### 2. Run Demo
```bash
python cryptvault_cli.py --demo
```

### 3. Analyze
```bash
# Crypto
python cryptvault_cli.py BTC 60 1d

# Stocks
python cryptvault_cli.py AAPL 60 1d

# With charts
python cryptvault_cli.py BTC 60 1d --verbose
```

---

## Supported Assets

**70+ Total Assets:**
- 50+ Cryptocurrencies (BTC, ETH, SOL, DOGE, LINK, etc.)
- 20+ Stocks (AAPL, TSLA, GOOGL, MSFT, etc.)

---

## Platform Support

✅ **Ubuntu/Linux** - Fully supported  
✅ **macOS** - Fully supported (including M1/M2)  
✅ **Windows** - Fully supported  
✅ **Python 3.8-3.12** - All versions

---

## Common Commands

```bash
# Demo
python cryptvault_cli.py --demo

# Version
python cryptvault_cli.py --version

# Status
python cryptvault_cli.py --status

# Help
python cryptvault_cli.py --help

# Analysis
python cryptvault_cli.py BTC 60 1d

# Verbose (with charts)
python cryptvault_cli.py BTC 60 1d --verbose

# Portfolio
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10

# Compare
python cryptvault_cli.py --compare BTC ETH SOL

# Interactive
python cryptvault_cli.py --interactive
```

---

## Documentation

- **[CLI vs Core](docs/CLI_VS_CORE.md)** - Detailed comparison
- **[Platform Support](docs/PLATFORM_SUPPORT.md)** - OS-specific guides
- **[Main README](docs/main_README.md)** - Complete documentation

---

## Need Help?

- GitHub: https://github.com/MeridianAlgo/Cryptvault
- Issues: https://github.com/MeridianAlgo/Cryptvault/issues
- Docs: See `docs/` folder

---

**Version:** 3.2.2-Public  
**License:** MIT
