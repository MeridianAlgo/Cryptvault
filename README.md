# CryptVault v3.2.4

CryptVault delivers AI-assisted cryptocurrency analysis with rich pattern detection and polished charting experiences.

## Quick Start

### Installation (Works on Ubuntu, macOS, Windows)

```bash
# Clone repository
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Install dependencies
pip install -r requirements.txt

# Run demo
python cryptvault_cli.py --demo

# Analyze Bitcoin
python cryptvault_cli.py BTC 60 1d

# Analyze stocks
python cryptvault_cli.py AAPL 60 1d

# Generate chart with pattern overlays
python generate_chart.py TSLA --days 90 --save tesla_chart.png
```

### Platform Support
- **Ubuntu/Linux** - Fully tested and supported
- **macOS** - Fully tested and supported  
- **Windows** - Fully tested and supported
- **Python 3.8-3.12** - All versions supported

## Features

- **50+ Chart Patterns** - Reversal, continuation, harmonic, candlestick patterns
- **ML Predictions** - Ensemble models with 8+ algorithms
- **120+ Supported Assets** - Major cryptocurrencies, stocks, and ETFs
- **Pattern Overlay Charts** - Matplotlib charts with visual pattern overlays
- **Terminal & Desktop Charts** - ASCII and matplotlib visualization
- **Portfolio Analysis** - Multi-asset comparison and optimization
- **Interactive CLI** - Command-line interface with live analysis
- **Cross-Platform** - Works on Ubuntu, macOS, and Windows

## Supported Assets

### Cryptocurrencies (50+)
BTC, ETH, USDT, BNB, SOL, XRP, USDC, ADA, AVAX, DOGE, TRX, DOT, MATIC, LINK, TON, SHIB, LTC, BCH, UNI, ATOM, XLM, XMR, ETC, HBAR, FIL, APT, ARB, VET, NEAR, ALGO, ICP, GRT, AAVE, MKR, SNX, SAND, MANA, AXS, FTM, THETA, EOS, XTZ, FLOW, EGLD, ZEC, CAKE, KLAY, RUNE, NEO, DASH, and more...

### Stocks (70+)
**Tech:** AAPL, TSLA, GOOGL, GOOG, MSFT, NVDA, AMZN, META, NFLX, AMD, INTC, CRM, ORCL, ADBE, CSCO, AVGO, QCOM, TXN, INTU, IBM, and more...

**Finance:** JPM, BAC, WFC, GS, MS, C, BLK, SCHW, AXP, USB, V, MA, PYPL, SQ, COIN

**Consumer:** WMT, HD, MCD, NKE, SBUX, TGT, COST, LOW, DIS, CMCSA

**Healthcare:** JNJ, UNH, PFE, ABBV, TMO, MRK, ABT, DHR, LLY, BMY

**Energy & Industrial:** XOM, CVX, COP, SLB, BA, CAT, GE, MMM, HON, UPS

**Transportation:** UBER, LYFT, ABNB, DAL, UAL, AAL

**ETFs:** SPY, QQQ, IWM, DIA, VOO, VTI, GLD, SLV

## 📚 Documentation

**[Complete Documentation Index](docs/INDEX.md)** - Full documentation with all guides and references

### Quick Links
- **[Quick Guide](QUICK_GUIDE.md)** - Fast reference guide
- **[Stock Support & Charts](docs/STOCK_SUPPORT_AND_CHARTS.md)** - Stock analysis and pattern overlays
- **[Interactive Chart Guide](docs/INTERACTIVE_CHART_GUIDE.md)** - Using interactive matplotlib windows
- **[CLI vs Core](docs/CLI_VS_CORE.md)** - Understanding the two entry points
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Complete development guide
- **[Platform Support](docs/PLATFORM_SUPPORT.md)** - OS compatibility guide

### Additional Resources
- **[Setup Guide](docs/setup/SETUP_GUIDE.md)** - Installation instructions
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute
- **[Security Policy](SECURITY.md)** - Security guidelines
- **[License](LICENSE)** - MIT License terms

## Chart Generation with Pattern Overlays

CryptVault now includes a powerful chart generation tool that creates professional candlestick charts with pattern overlays using matplotlib:

```bash
# Open interactive chart window (default)
python generate_chart.py BTC
python generate_chart.py AAPL --days 60
python generate_chart.py TSLA --days 90

# Save chart to file (optional)
python generate_chart.py GOOGL --days 120 --save google.png
```

**Features:**
- Interactive charts with zoom, pan, and navigation controls
- Professional candlestick charts with volume bars
- Visual pattern overlays (triangles, rectangles, channels, divergences, etc.)
- Zoom into patterns for detailed examination
- Save charts as high-quality PNG images
- Beautiful dark theme optimized for readability
- Support for both stocks and cryptocurrencies
- Automatic pattern detection and visualization
- Mouse and keyboard controls for navigation

**Pattern Overlay Types:**
- Triangles (Ascending, Descending, Symmetrical, Expanding)
- Rectangles and Channels
- Wedges (Rising, Falling)
- Flags and Pennants
- Head and Shoulders
- Double/Triple Tops and Bottoms
- Divergence Patterns
- Diamond Patterns

## CLI vs Core Application

- **`cryptvault_cli.py`** is the interactive command-line entry point. It orchestrates data ingestion, pattern recognition, model execution, and optional desktop visualization for day-to-day usage.
- **`cryptvault.py`** focuses on terminal-based chart rendering. It offers an expressive ASCII dashboard and low-level access for custom scripts or integrations that need the charting layer without the full CLI orchestration.
- **`generate_chart.py`** creates professional matplotlib charts with pattern overlays. Perfect for generating reports, presentations, or detailed technical analysis with visual pattern indicators.

Use the CLI for end-to-end analysis, multi-asset comparisons, and automation. Use the core script when you need lightweight chart output. Use generate_chart.py when you need publication-quality charts with pattern overlays.

## Repository Structure

```text
.
├── config/                  # Environment templates and overrides
├── cryptvault/              # Core analysis engine, indicators, ML modules
├── docs/                    # Primary documentation bundle
│   ├── main_README.md       # Detailed platform overview & usage
│   ├── setup/               # Installation & verification guides
│   ├── policies/            # Governance and contribution docs
│   └── ...                  # Additional deep dives and references
├── logs/                    # Runtime logs (`cryptvault.log`)
├── tests/                   # Pytest suite for parsers, indicators, ML
├── cryptvault.py            # Terminal charting application
├── cryptvault_cli.py        # Full-featured CLI and desktop launcher
├── requirements.txt         # Python dependencies
├── setup.py                 # Packaging metadata
└── LICENSE                  # MIT license terms
```

## Next Steps

1. Review `docs/main_README.md` for advanced usage patterns and examples.
2. Copy `config/.env.example` to `.env` if you need to override defaults.
3. Run `python -m pytest tests/` to validate installation.
