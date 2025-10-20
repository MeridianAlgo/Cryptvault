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

# Generate chart with pattern overlays
python generate_chart.py TSLA --days 90 --save tesla_chart.png
```

---

## Supported Assets

**120+ Total Assets:**
- 50+ Cryptocurrencies (BTC, ETH, SOL, DOGE, LINK, etc.)
- 70+ Stocks (AAPL, TSLA, GOOGL, MSFT, NVDA, JPM, etc.)
- ETFs (SPY, QQQ, IWM, DIA, VOO, VTI, GLD, SLV)

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

# Generate chart with pattern overlays
python generate_chart.py BTC --days 60
python generate_chart.py AAPL --days 90 --save apple_chart.png
python generate_chart.py TSLA --days 120 --interval 1d --save tesla.png
```

---

## Documentation

- **[CLI vs Core](docs/CLI_VS_CORE.md)** - Detailed comparison
- **[Platform Support](docs/PLATFORM_SUPPORT.md)** - OS-specific guides
- **[Stock Support & Charts](docs/STOCK_SUPPORT_AND_CHARTS.md)** - Stock analysis and pattern overlays
- **[Main README](docs/main_README.md)** - Complete documentation

---

## Need Help?

- GitHub: https://github.com/MeridianAlgo/Cryptvault
- Issues: https://github.com/MeridianAlgo/Cryptvault/issues
- Docs: See `docs/` folder

---

**Version:** 3.2.4  
**License:** MIT


---

## Related Documentation

### Getting Started
- [Main README](../README.md) - Project overview
- [Setup Complete](../SETUP_COMPLETE.md) - Setup summary
- [Setup Guide](setup/SETUP_GUIDE.md) - Installation instructions

### Features
- [Stock Support & Charts](STOCK_SUPPORT_AND_CHARTS.md) - Stock analysis guide
- [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md) - Interactive windows
- [CLI vs Core](CLI_VS_CORE.md) - Understanding entry points
- [Platform Support](PLATFORM_SUPPORT.md) - OS compatibility

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md)
