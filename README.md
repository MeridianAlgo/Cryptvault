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

# Analyze Bitcoin (opens interactive chart by default)
python cryptvault_cli.py BTC 60 1d

# Save chart to file
python cryptvault_cli.py AAPL 90 1d --save-chart apple.png

# Text-only analysis (no chart)
python cryptvault_cli.py ETH 60 1d --no-chart
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
- **[Quick Guide](docs/QUICK_GUIDE.md)** - Fast reference guide
- **[Stock Support & Charts](docs/STOCK_SUPPORT_AND_CHARTS.md)** - Stock analysis and pattern overlays
- **[Interactive Chart Guide](docs/INTERACTIVE_CHART_GUIDE.md)** - Using interactive matplotlib windows
- **[CLI vs Core](docs/CLI_VS_CORE.md)** - Understanding the two entry points
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Complete development guide
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Testing and CI/CD documentation

### Additional Resources
- **[Platform Support](docs/PLATFORM_SUPPORT.md)** - OS compatibility guide
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute
- **[Security Policy](SECURITY.md)** - Security guidelines
- **[License](LICENSE)** - MIT License terms

## Chart Generation with Pattern Overlays

**CryptVault CLI now automatically generates matplotlib charts with pattern overlays!**

```bash
# Default: Opens interactive chart window with pattern overlays
python cryptvault_cli.py BTC 60 1d

# Save chart to file instead of displaying
python cryptvault_cli.py AAPL 90 1d --save-chart apple.png

# Disable chart generation (text-only analysis)
python cryptvault_cli.py ETH 60 1d --no-chart
```

**Chart Features:**
- Professional candlestick visualization
- All detected patterns overlaid on chart
- Interactive zoom, pan, and navigation
- Volume bars with color coding
- Support/resistance levels
- Dark theme optimized for readability

You can also use the standalone chart generator:

```bash
# Open interactive chart window
python generate_chart.py BTC --days 60

# Save chart to file
python generate_chart.py TSLA --days 90 --save tesla.png
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

## CLI Application

- **`cryptvault_cli.py`** is the main command-line interface with integrated chart generation. It provides:
  - Interactive analysis with pattern detection
  - Professional matplotlib charts with pattern overlays
  - Multi-asset comparisons and portfolio analysis
  - Desktop visualization and chart export
  - ML predictions and technical indicators

Use `cryptvault_cli.py` for all analysis needs - it now includes chart generation with the `--chart` flag.

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
