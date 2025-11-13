# CryptVault v4.0.0

[![CI](https://github.com/MeridianAlgo/Cryptvault/workflows/CI/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MeridianAlgo/Cryptvault/branch/main/graph/badge.svg)](https://codecov.io/gh/MeridianAlgo/Cryptvault)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Advanced AI-Powered Cryptocurrency & Stock Analysis Platform**

CryptVault is a production-ready, enterprise-grade cryptocurrency and stock analysis platform featuring advanced pattern detection, machine learning predictions, and professional charting capabilities. Built with industry best practices, comprehensive documentation, and robust error handling.

## ✨ Key Features

- **50+ Chart Patterns** - Reversal, continuation, harmonic, and candlestick patterns with confidence scoring
- **ML-Powered Predictions** - Ensemble models combining 8+ algorithms for price forecasting
- **120+ Supported Assets** - Major cryptocurrencies, stocks, and ETFs
- **Professional Charts** - Interactive matplotlib visualizations with pattern overlays
- **Real-Time Analysis** - Live pattern detection and technical indicator calculations
- **Portfolio Management** - Multi-asset comparison and optimization tools
- **Production-Ready** - Enterprise-grade code quality with 85%+ test coverage
- **Cross-Platform** - Full support for Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest tests/ --run
```

### Basic Usage

```bash
# Run interactive demo
python cryptvault_cli.py --demo

# Analyze Bitcoin (opens interactive chart)
python cryptvault_cli.py BTC 60 1d

# Analyze Apple stock with chart export
python cryptvault_cli.py AAPL 90 1d --save-chart apple_analysis.png

# Text-only analysis (no chart window)
python cryptvault_cli.py ETH 60 1d --no-chart

# Compare multiple assets
python cryptvault_cli.py BTC ETH AAPL --days 30
```

### Python API

```python
from cryptvault.core.analyzer import PatternAnalyzer
from cryptvault.config import Config

# Initialize analyzer
config = Config.load('production')
analyzer = PatternAnalyzer(config)

# Analyze a ticker
result = analyzer.analyze_ticker('BTC', days=60, interval='1d')

# Access results
print(f"Found {len(result.patterns)} patterns")
for pattern in result.patterns:
    print(f"  {pattern.pattern_type}: {pattern.confidence:.2%} confidence")

# ML predictions
if result.ml_predictions:
    print(f"7-day prediction: ${result.ml_predictions['price_7d']:.2f}")
```

## 📂 Project Structure

```
cryptvault/
├── cli/                       # Command-line interface
│   ├── commands.py           # CLI command implementations
│   ├── formatters.py         # Output formatting utilities
│   └── validators.py         # Input validation
├── core/                      # Core business logic
│   ├── analyzer.py           # Main analysis orchestrator
│   └── portfolio.py          # Portfolio management
├── data/                      # Data layer
│   ├── models.py             # Data models (PricePoint, PriceDataFrame)
│   ├── fetchers.py           # Data fetching (yfinance, ccxt)
│   ├── cache.py              # Data caching layer
│   └── validators.py         # Data validation
├── indicators/                # Technical indicators
│   ├── trend.py              # Moving averages, trend analysis
│   ├── momentum.py           # RSI, MACD, Stochastic
│   ├── volatility.py         # Bollinger Bands, ATR
│   └── volume.py             # Volume indicators
├── patterns/                  # Pattern detection
│   ├── base.py               # Base pattern detector
│   ├── reversal.py           # Head & shoulders, double tops/bottoms
│   ├── continuation.py       # Triangles, flags, pennants
│   ├── harmonic.py           # Gartley, Butterfly, Bat patterns
│   └── candlestick.py        # Candlestick patterns
├── ml/                        # Machine learning
│   ├── features.py           # Feature engineering
│   ├── models.py             # ML model implementations
│   ├── predictor.py          # Prediction interface
│   └── cache.py              # Prediction caching
├── visualization/             # Charting
│   ├── charts.py             # Chart generation
│   └── formatters.py         # Data formatting
├── utils/                     # Utilities
│   ├── logging.py            # Logging configuration
│   ├── decorators.py         # Common decorators
│   └── helpers.py            # Helper functions
├── config.py                  # Configuration management
├── exceptions.py              # Custom exception hierarchy
└── constants.py               # System-wide constants
```

## 💡 Use Cases

- **Technical Analysis** - Identify chart patterns and trends in real-time
- **Price Prediction** - ML-powered forecasting for informed decision-making
- **Portfolio Optimization** - Compare and analyze multiple assets
- **Research & Education** - Learn technical analysis and pattern recognition
- **Automated Trading Research** - Backtest strategies with historical patterns
- **Market Monitoring** - Track multiple assets with automated alerts

## 📊 Supported Assets

### Cryptocurrencies (50+)
BTC, ETH, USDT, BNB, SOL, XRP, USDC, ADA, AVAX, DOGE, TRX, DOT, MATIC, LINK, TON, SHIB, LTC, BCH, UNI, ATOM, XLM, XMR, ETC, HBAR, FIL, APT, ARB, VET, NEAR, ALGO, ICP, GRT, AAVE, MKR, SNX, SAND, MANA, AXS, FTM, THETA, EOS, XTZ, FLOW, EGLD, ZEC, CAKE, KLAY, RUNE, NEO, DASH, and more...

### Stocks (70+)
**Technology:** AAPL, TSLA, GOOGL, GOOG, MSFT, NVDA, AMZN, META, NFLX, AMD, INTC, CRM, ORCL, ADBE, CSCO, AVGO, QCOM, TXN, INTU, IBM

**Finance:** JPM, BAC, WFC, GS, MS, C, BLK, SCHW, AXP, USB, V, MA, PYPL, SQ, COIN

**Consumer:** WMT, HD, MCD, NKE, SBUX, TGT, COST, LOW, DIS, CMCSA

**Healthcare:** JNJ, UNH, PFE, ABBV, TMO, MRK, ABT, DHR, LLY, BMY

**Energy & Industrial:** XOM, CVX, COP, SLB, BA, CAT, GE, MMM, HON, UPS

**Transportation:** UBER, LYFT, ABNB, DAL, UAL, AAL

**ETFs:** SPY, QQQ, IWM, DIA, VOO, VTI, GLD, SLV

## 🎯 Pattern Detection

CryptVault detects 50+ chart patterns across multiple categories:

### Reversal Patterns
- Head and Shoulders (Regular & Inverse)
- Double Top / Double Bottom
- Triple Top / Triple Bottom
- Rounding Top / Rounding Bottom
- V-Top / V-Bottom

### Continuation Patterns
- Ascending / Descending / Symmetrical Triangles
- Rising / Falling Wedges
- Bull / Bear Flags
- Pennants
- Rectangles

### Harmonic Patterns
- Gartley Pattern
- Butterfly Pattern
- Bat Pattern
- Crab Pattern
- ABCD Pattern

### Candlestick Patterns
- Doji, Hammer, Shooting Star
- Engulfing Patterns
- Morning / Evening Star
- Three White Soldiers / Three Black Crows
- And many more...

## 📈 Technical Indicators

### Trend Indicators
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Weighted Moving Average (WMA)
- Moving Average Convergence Divergence (MACD)

### Momentum Indicators
- Relative Strength Index (RSI)
- Stochastic Oscillator
- Commodity Channel Index (CCI)
- Rate of Change (ROC)

### Volatility Indicators
- Bollinger Bands
- Average True Range (ATR)
- Standard Deviation
- Keltner Channels

### Volume Indicators
- On-Balance Volume (OBV)
- Volume Weighted Average Price (VWAP)
- Accumulation/Distribution Line
- Money Flow Index (MFI)

## ⚙️ Configuration

CryptVault supports flexible configuration through YAML files and environment variables:

```bash
# Copy example configuration
cp config/.env.example config/.env

# Edit configuration
nano config/settings.yaml
```

### Environment Variables

```bash
# Network configuration
export CRYPTVAULT_NETWORK_TIMEOUT=30
export CRYPTVAULT_NETWORK_MAX_RETRIES=3

# Cache configuration
export CRYPTVAULT_CACHE_ENABLED=true
export CRYPTVAULT_CACHE_TTL=300

# Logging configuration
export CRYPTVAULT_LOG_LEVEL=INFO
export CRYPTVAULT_LOG_FILE=logs/cryptvault.log

# Analysis configuration
export CRYPTVAULT_DEFAULT_DAYS=60
export CRYPTVAULT_ML_ENABLED=true

# API keys (optional)
export CRYPTOCOMPARE_API_KEY=your_api_key_here
```

### Configuration Files

- `config/settings.yaml` - Base configuration
- `config/settings.development.yaml` - Development overrides
- `config/settings.testing.yaml` - Testing overrides
- `config/logging.yaml` - Logging configuration

## 🧪 Testing

CryptVault includes comprehensive test coverage (85%+):

```bash
# Run all tests
python -m pytest tests/

# Run with coverage report
python -m pytest tests/ --cov=cryptvault --cov-report=html

# Run specific test categories
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/integration/   # Integration tests only

# Run with verbose output
python -m pytest tests/ -v
```

## 📚 Documentation

### Getting Started
- [Quick Start Guide](docs/QUICK_GUIDE.md) - Get up and running in 5 minutes
- [Platform Support](docs/PLATFORM_SUPPORT.md) - Windows, macOS, Linux compatibility
- [Installation Guide](docs/setup/SETUP_GUIDE.md) - Detailed installation instructions

### Core Documentation
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Development setup and guidelines
- [Testing Guide](docs/TESTING_GUIDE.md) - Running and writing tests

### User Guides
- [CLI Guide](docs/CLI_VS_CORE.md) - Command-line interface usage
- [Interactive Charts](docs/INTERACTIVE_CHART_GUIDE.md) - Chart features and controls
- [Stock Support](docs/STOCK_SUPPORT_AND_CHARTS.md) - Stock analysis features

### Contributing
- [Contributing Guidelines](docs/CONTRIBUTING.md) - How to contribute
- [Code of Conduct](docs/policies/CODE_OF_CONDUCT.md) - Community guidelines
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

### Additional Resources
- [Changelog](docs/CHANGELOG.md) - Version history
- [License](LICENSE) - MIT License terms

## 📊 Chart Generation

CryptVault generates professional matplotlib charts with pattern overlays:

```bash
# Interactive chart window (default)
python cryptvault_cli.py BTC 60 1d

# Save chart to file
python cryptvault_cli.py AAPL 90 1d --save-chart apple_analysis.png

# Text-only analysis (no chart)
python cryptvault_cli.py ETH 60 1d --no-chart

# Standalone chart generator
python generate_chart.py BTC --days 60 --save btc_chart.png
```

### Chart Features
- Professional candlestick visualization with volume bars
- All detected patterns overlaid with annotations
- Interactive zoom, pan, and navigation controls
- Support/resistance levels and trend lines
- Dark theme optimized for readability
- High-quality PNG export
- Mouse and keyboard controls
- Pattern confidence indicators

## 🛠️ Development

### Prerequisites
- Python 3.8 - 3.12
- pip (Python package manager)
- Git

### Development Setup

```bash
# Clone repository
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/ -v

# Run linters
pylint cryptvault/
mypy cryptvault/
flake8 cryptvault/
```

### Code Quality Standards
- PEP 8 compliance
- Type hints for all functions
- 85%+ test coverage
- Comprehensive docstrings
- Maximum cyclomatic complexity: 10
- No code duplication > 5 lines

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t cryptvault:4.0.0 .

# Run container
docker run -it --rm cryptvault:4.0.0 BTC 60 1d

# Using docker-compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔒 Security

CryptVault implements comprehensive security measures:

- **Input Validation**: Whitelist-based ticker validation with injection prevention
- **Credential Management**: Secure storage via environment variables with automatic redaction
- **Rate Limiting**: Token bucket algorithm with exponential backoff
- **Secure Logging**: Automatic redaction of sensitive data in logs
- **OWASP Compliance**: Addresses OWASP Top 10 security risks
- **Security Auditing**: Automated scanning with `bandit` and `safety`

### Running Security Audit

```bash
python scripts/security_audit.py
```

### Security Best Practices

1. Store API keys in environment variables (never hardcode)
2. Use `.env` file for local development (add to `.gitignore`)
3. Enable strict mode for input validation in production
4. Rotate credentials every 90 days
5. Run security audit before deployment

See [Security Documentation](docs/SECURITY.md) for detailed information.

Report security vulnerabilities to: security@meridianalgo.com

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built by the MeridianAlgo Algorithmic Research Team
- Powered by yfinance, ccxt, and scikit-learn
- Chart visualization with matplotlib
- Pattern detection algorithms based on technical analysis research

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/MeridianAlgo/Cryptvault/issues)
- Discussions: [GitHub Discussions](https://github.com/MeridianAlgo/Cryptvault/discussions)
- Email: support@meridianalgo.com

## 🗺️ Roadmap

- [ ] Real-time WebSocket data streaming
- [ ] Advanced portfolio optimization algorithms
- [ ] Custom indicator builder
- [ ] Backtesting framework
- [ ] Web dashboard interface
- [ ] Mobile app support
- [ ] Additional ML models (Transformer, GAN)
- [ ] Social sentiment analysis integration

---

**Disclaimer:** CryptVault is for educational and research purposes only. Not financial advice. Always do your own research before making investment decisions.
