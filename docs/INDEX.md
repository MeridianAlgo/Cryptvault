# CryptVault Documentation Index

Complete documentation for CryptVault pattern analysis system.

## Quick Start

- [Main README](../README.md) - Project overview and quick start
- [Quick Guide](../QUICK_GUIDE.md) - Fast reference guide
- [Installation Guide](setup/SETUP_GUIDE.md) - Complete installation instructions

## Core Documentation

### Getting Started
- [CLI vs Core](CLI_VS_CORE.md) - Understanding the two entry points
- [Platform Support](PLATFORM_SUPPORT.md) - Ubuntu, macOS, Windows compatibility
- [Installation Verification](setup/INSTALLATION_VERIFIED.md) - Verify your setup

### Features & Usage
- [Stock Support and Charts](STOCK_SUPPORT_AND_CHARTS.md) - Stock analysis and pattern overlays
- [Interactive Charts](INTERACTIVE_CHART_GUIDE.md) - Using interactive matplotlib windows
- [Matplotlib Toolbar Guide](MATPLOTLIB_TOOLBAR_GUIDE.md) - Understanding the toolbar buttons
- [Interactive Features Summary](INTERACTIVE_FEATURES_SUMMARY.md) - Quick interactive reference
- [Chart Generation Results](CHART_GENERATION_RESULTS.md) - Example outputs

### Technical Documentation
- [Developer Guide](DEVELOPER_GUIDE.md) - Complete development guide
- [Enhanced ML System](ENHANCED_ML_SYSTEM.md) - Machine learning details
- [Beautiful Candlestick Charts](BEAUTIFUL_CANDLESTICK_CHARTS.md) - Charting system
- [Final System Summary](FINAL_SYSTEM_SUMMARY.md) - System capabilities

### Project Information
- [Changelog](CHANGELOG.md) - Version history
- [Stock Support Changelog](CHANGELOG_STOCK_SUPPORT.md) - Stock feature updates
- [Release Notes v3.1.0](RELEASE_NOTES_3.1.0.md) - Latest release
- [Project Status](PROJECT_STATUS.md) - Current development status

### Policies & Contributing
- [Contributing Guidelines](../CONTRIBUTING.md) - How to contribute
- [Code of Conduct](policies/CODE_OF_CONDUCT.md) - Community guidelines
- [Contributing Policy](policies/CONTRIBUTING.md) - Detailed contribution policy
- [Security Policy](../SECURITY.md) - Security guidelines

## Feature Guides

### Pattern Analysis
- 50+ chart patterns supported
- Geometric patterns (triangles, rectangles, wedges)
- Reversal patterns (head & shoulders, double tops/bottoms)
- Harmonic patterns (Gartley, Butterfly, ABCD)
- Candlestick patterns
- Divergence patterns

### Chart Generation
- Interactive matplotlib windows
- Pattern overlay visualization
- Professional candlestick charts
- Volume analysis
- Save to PNG files
- Zoom and pan controls

### Stock Market Support
- 129 supported assets
- 50+ cryptocurrencies
- 70+ stocks across sectors
- 8 major ETFs
- Real-time data fetching
- Multiple timeframes

### Machine Learning
- Ensemble prediction models
- 11 ML algorithms
- Price forecasting
- Trend prediction
- Pattern confidence scoring
- Model performance tracking

## API Reference

### Command Line Interface

#### cryptvault_cli.py
```bash
python cryptvault_cli.py SYMBOL DAYS INTERVAL [OPTIONS]
```

Options:
- `--demo` - Run demonstration
- `--version` - Show version
- `--status` - System status
- `--portfolio` - Portfolio analysis
- `--compare` - Compare assets
- `--interactive` - Interactive mode
- `--verbose` - Detailed output

#### generate_chart.py
```bash
python generate_chart.py SYMBOL [OPTIONS]
```

Options:
- `--days DAYS` - Historical data days (default: 30)
- `--interval INTERVAL` - Data interval: 1h, 4h, 1d, 1w (default: 1d)
- `--save FILENAME` - Save to file (default: display window)

### Python API

#### Pattern Analysis
```python
from cryptvault.analyzer import PatternAnalyzer

analyzer = PatternAnalyzer()
results = analyzer.analyze_ticker('BTC', days=60, interval='1d')
```

#### Data Fetching
```python
from cryptvault.data.package_fetcher import PackageDataFetcher

fetcher = PackageDataFetcher()
data = fetcher.fetch_historical_data('AAPL', days=90, interval='1d')
```

#### Pattern Overlay
```python
from cryptvault.visualization.pattern_overlay import PatternOverlay

overlay = PatternOverlay(ax)
overlay.draw_pattern(pattern, dates, opens, highs, lows, closes)
```

## Examples

### Basic Usage
```bash
# Analyze Bitcoin
python cryptvault_cli.py BTC 60 1d

# Analyze Apple stock
python cryptvault_cli.py AAPL 90 1d

# Generate interactive chart
python generate_chart.py TSLA --days 60

# Save chart to file
python generate_chart.py SPY --days 180 --save sp500.png
```

### Advanced Usage
```bash
# Portfolio analysis
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10 AAPL:5

# Compare assets
python cryptvault_cli.py --compare BTC ETH SOL

# Interactive mode
python cryptvault_cli.py --interactive

# Demo mode
python cryptvault_cli.py --demo
```

## Supported Assets

### Cryptocurrencies (50+)
BTC, ETH, SOL, XRP, ADA, DOGE, MATIC, LINK, UNI, AVAX, and more

### Technology Stocks (20)
AAPL, TSLA, GOOGL, GOOG, MSFT, NVDA, AMZN, META, NFLX, AMD, INTC, CRM, ORCL, ADBE, CSCO, AVGO, QCOM, TXN, INTU, IBM

### Financial Stocks (15)
JPM, BAC, WFC, GS, MS, C, BLK, SCHW, AXP, USB, V, MA, PYPL, SQ, COIN

### Consumer Stocks (10)
WMT, HD, MCD, NKE, SBUX, TGT, COST, LOW, DIS, CMCSA

### Healthcare Stocks (10)
JNJ, UNH, PFE, ABBV, TMO, MRK, ABT, DHR, LLY, BMY

### Energy & Industrial (10)
XOM, CVX, COP, SLB, BA, CAT, GE, MMM, HON, UPS

### Transportation (6)
UBER, LYFT, ABNB, DAL, UAL, AAL

### ETFs (8)
SPY, QQQ, IWM, DIA, VOO, VTI, GLD, SLV

## Troubleshooting

### Common Issues

**Installation Problems**
- See [Setup Guide](setup/SETUP_GUIDE.md)
- Check [Platform Support](PLATFORM_SUPPORT.md)

**Data Fetching Issues**
- Verify internet connection
- Check ticker symbol validity
- Try different data source

**Chart Display Problems**
- See [Interactive Chart Guide](INTERACTIVE_CHART_GUIDE.md)
- Check matplotlib backend
- Try saving to file instead

**Pattern Detection Issues**
- Increase data period
- Adjust sensitivity settings
- Check data quality

## Development

### Setup Development Environment
```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
python -m pytest tests/
```

### Running Tests
```bash
# All tests
python -m pytest tests/

# Specific test
python -m pytest tests/test_parsers.py

# With coverage
python -m pytest tests/ --cov=cryptvault
```

### Code Style
- Follow PEP 8
- Use type hints
- Document functions
- Write tests

## Resources

### External Links
- [GitHub Repository](https://github.com/MeridianAlgo/Cryptvault)
- [Issue Tracker](https://github.com/MeridianAlgo/Cryptvault/issues)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [matplotlib Documentation](https://matplotlib.org/)

### Community
- Report bugs on GitHub Issues
- Contribute via Pull Requests
- Follow coding guidelines
- Respect Code of Conduct

## Version Information

**Current Version**: 3.3.0
**Python Support**: 3.8 - 3.12
**Platforms**: Windows, macOS, Linux
**License**: MIT

## Navigation

- [Navigation Map](NAVIGATION_MAP.md) - Complete navigation guide for all documentation
- [Back to Main README](../README.md)
- [Quick Guide](QUICK_GUIDE.md)
- [Setup Complete](../SETUP_COMPLETE.md)
- [Contributing](../CONTRIBUTING.md)
- [License](../LICENSE)
- [Security Policy](../SECURITY.md)

---

## Related Documentation

All documentation pages are interconnected with navigation footers. Each page includes:
- Related Documentation section with categorized links
- Quick navigation bar at the bottom
- Links to Documentation Index and Main README

See [Navigation Map](NAVIGATION_MAP.md) for complete navigation structure.

---

[🗺️ Navigation Map](NAVIGATION_MAP.md) | [🏠 Main README](../README.md) | [⚡ Quick Guide](QUICK_GUIDE.md)

---

Made with care by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)
