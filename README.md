# CryptVault v3.2.0-Public

CryptVault delivers AI-assisted cryptocurrency analysis with rich pattern detection and polished charting experiences.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
python cryptvault_cli.py --demo

# Analyze Bitcoin
python cryptvault_cli.py BTC 60 1d

# Analyze stocks
python cryptvault_cli.py AAPL 60 1d
```

## Features

- **50+ Chart Patterns** - Reversal, continuation, harmonic, candlestick patterns
- **ML Predictions** - Ensemble models with 8+ algorithms
- **70+ Supported Assets** - Major cryptocurrencies and popular stocks
- **Terminal & Desktop Charts** - ASCII and matplotlib visualization
- **Portfolio Analysis** - Multi-asset comparison and optimization
- **Interactive CLI** - Command-line interface with live analysis

## Supported Assets

### Cryptocurrencies (50+)
BTC, ETH, USDT, BNB, SOL, XRP, USDC, ADA, AVAX, DOGE, TRX, DOT, MATIC, LINK, TON, SHIB, LTC, BCH, UNI, ATOM, XLM, XMR, ETC, HBAR, FIL, APT, ARB, VET, NEAR, ALGO, ICP, GRT, AAVE, MKR, SNX, SAND, MANA, AXS, FTM, THETA, EOS, XTZ, FLOW, EGLD, ZEC, CAKE, KLAY, RUNE, NEO, DASH, and more...

### Stocks (20+)
AAPL, TSLA, GOOGL, MSFT, NVDA, AMZN, META, NFLX, AMD, INTC, COIN, SQ, PYPL, V, MA, JPM, BAC, WMT, DIS, UBER, and more...

## Documentation

### Core Documentation
- **[Main README](docs/main_README.md)** - Complete product overview and features
- **[Final System Summary](docs/FINAL_SYSTEM_SUMMARY.md)** - System capabilities and achievements
- **[Enhanced ML System](docs/ENHANCED_ML_SYSTEM.md)** - Machine learning implementation details
- **[Beautiful Candlestick Charts](docs/BEAUTIFUL_CANDLESTICK_CHARTS.md)** - Charting system documentation
- **[Changelog](docs/CHANGELOG.md)** - Version history and updates
- **[Release Notes v3.1.0](docs/RELEASE_NOTES_3.1.0.md)** - Latest release information
- **[Project Status](docs/PROJECT_STATUS.md)** - Current development status
- **[Documentation Index](docs/README.md)** - Complete documentation index

### Setup & Installation
- **[Setup Guide](docs/setup/SETUP_GUIDE.md)** - Complete installation guide
- **[Installation Verification](docs/setup/INSTALLATION_VERIFIED.md)** - Verify your installation

### Policies & Contributing
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to CryptVault
- **[Code of Conduct](docs/policies/CODE_OF_CONDUCT.md)** - Community guidelines
- **[Contributing Policy](docs/policies/CONTRIBUTING.md)** - Detailed contribution policy
- **[Security Policy](SECURITY.md)** - Security guidelines and reporting
- **[License](LICENSE)** - MIT License terms

## CLI vs Core Application

- **`cryptvault_cli.py`** is the interactive command-line entry point. It orchestrates data ingestion, pattern recognition, model execution, and optional desktop visualization for day-to-day usage.
- **`cryptvault.py`** focuses on terminal-based chart rendering. It offers an expressive ASCII dashboard and low-level access for custom scripts or integrations that need the charting layer without the full CLI orchestration.

Use the CLI for end-to-end analysis, multi-asset comparisons, and automation. Use the core script when you need lightweight chart output or want to embed CryptVault visuals in other tooling.

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
