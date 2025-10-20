# CryptVault CLI vs Core: Understanding the Difference

CryptVault provides two entry points for different use cases:

## cryptvault_cli.py - Full-Featured CLI Application

**Purpose:** Complete command-line interface with all features

**Features:**
- ✅ Full pattern analysis
- ✅ ML predictions with ensemble models
- ✅ Portfolio analysis
- ✅ Multi-asset comparison
- ✅ Interactive mode
- ✅ Desktop charts
- ✅ Prediction accuracy tracking
- ✅ Live analysis
- ✅ Status checks
- ✅ Demo mode

**Usage:**
```bash
# Basic analysis
python cryptvault_cli.py BTC 60 1d

# Advanced features
python cryptvault_cli.py --demo
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10
python cryptvault_cli.py --compare BTC ETH ADA
python cryptvault_cli.py --interactive
python cryptvault_cli.py --desktop
python cryptvault_cli.py --accuracy
python cryptvault_cli.py --status
```

**Best For:**
- Daily trading analysis
- Portfolio management
- Multi-asset comparison
- Interactive exploration
- Full-featured analysis

---

## cryptvault.py - Terminal Charts Application

**Purpose:** Lightweight terminal-based charting with pattern visualization

**Features:**
- ✅ Terminal ASCII charts
- ✅ Pattern detection
- ✅ Basic ML predictions
- ✅ Multi-asset analysis
- ✅ Minimalist output
- ✅ Fast execution

**Usage:**
```bash
# Single asset
python cryptvault.py BTC 60 1d

# Multiple assets
python cryptvault.py -m BTC ETH SOL

# Verbose mode
python cryptvault.py BTC 60 1d -v
```

**Best For:**
- Quick chart visualization
- Terminal-only environments
- Scripting and automation
- Lightweight analysis
- Embedding in other tools

---

## Quick Comparison

| Feature | cryptvault_cli.py | cryptvault.py |
|---------|-------------------|---------------|
| Pattern Detection | ✅ Full | ✅ Full |
| ML Predictions | ✅ Ensemble | ✅ Basic |
| Terminal Charts | ✅ Yes | ✅ Yes |
| Desktop Charts | ✅ Yes | ❌ No |
| Portfolio Analysis | ✅ Yes | ❌ No |
| Interactive Mode | ✅ Yes | ❌ No |
| Multi-Asset Compare | ✅ Yes | ✅ Limited |
| Prediction Tracking | ✅ Yes | ❌ No |
| Status Checks | ✅ Yes | ❌ No |
| Demo Mode | ✅ Yes | ❌ No |
| File Size | ~500 lines | ~800 lines |
| Startup Time | ~1s | ~0.5s |
| Memory Usage | ~150MB | ~100MB |

---

## When to Use Each

### Use cryptvault_cli.py when:
- You need full analysis features
- You want portfolio management
- You need interactive exploration
- You want desktop charts
- You need prediction tracking
- You're doing daily trading analysis

### Use cryptvault.py when:
- You only need charts
- You're in a terminal-only environment
- You're scripting/automating
- You want faster startup
- You need lightweight analysis
- You're embedding in other tools

---

## Examples

### Full Analysis (cryptvault_cli.py)
```bash
# Complete analysis with all features
python cryptvault_cli.py BTC 60 1d --verbose

# Portfolio analysis
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10 ADA:1000

# Compare multiple assets
python cryptvault_cli.py --compare BTC ETH SOL LINK

# Interactive mode
python cryptvault_cli.py --interactive
cryptvault> analyze BTC 60 1d
cryptvault> portfolio BTC:0.5 ETH:10
cryptvault> compare BTC ETH
cryptvault> exit
```

### Quick Charts (cryptvault.py)
```bash
# Quick chart view
python cryptvault.py BTC 60 1d

# Multiple assets
python cryptvault.py -m BTC ETH SOL

# Verbose with patterns
python cryptvault.py BTC 60 1d -v
```

---

## Recommendation

**For most users:** Use `cryptvault_cli.py`
- It's the main application
- Has all features
- Better user experience
- More documentation

**For advanced users:** Use `cryptvault.py`
- When you need just charts
- For scripting/automation
- In resource-constrained environments

---

## Migration

If you're using `cryptvault.py` and want more features:

```bash
# Old way (cryptvault.py)
python cryptvault.py BTC 60 1d

# New way (cryptvault_cli.py) - same result + more features
python cryptvault_cli.py BTC 60 1d
```

All commands are compatible, just switch the filename!

---

## Technical Details

### cryptvault_cli.py Architecture
```
cryptvault_cli.py
├── PatternAnalyzer (full)
├── MLPredictor (ensemble)
├── PortfolioAnalyzer
├── DesktopCharts
├── PredictionCache
└── Interactive Shell
```

### cryptvault.py Architecture
```
cryptvault.py
├── PatternAnalyzer (full)
├── MLPredictor (basic)
├── TerminalChart
└── AdvancedCryptoCharts
```

---

## Summary

- **cryptvault_cli.py** = Full-featured CLI application (recommended)
- **cryptvault.py** = Lightweight terminal charts (for specific use cases)

Both are maintained and fully functional. Choose based on your needs!


---

## Related Documentation

### Getting Started
- [Main README](../README.md) - Project overview
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference
- [Setup Guide](setup/SETUP_GUIDE.md) - Installation instructions

### Features
- [Stock Support & Charts](STOCK_SUPPORT_AND_CHARTS.md) - Stock analysis guide
- [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md) - Interactive windows
- [Developer Guide](DEVELOPER_GUIDE.md) - Development documentation
- [Platform Support](PLATFORM_SUPPORT.md) - OS compatibility

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Changelog](CHANGELOG.md) - Version history
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines

---

[📚 Documentation Index](INDEX.md) | [🏠 Main README](../README.md) | [⚡ Quick Guide](../QUICK_GUIDE.md)
