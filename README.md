# CryptVault - AI-Powered Cryptocurrency Analysis Platform

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-5.0.0-brightgreen.svg)](https://github.com/MeridianAlgo/Cryptvault/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/MeridianAlgo/Cryptvault/workflows/Tests/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/tests.yml)
[![Lint](https://github.com/MeridianAlgo/Cryptvault/workflows/Lint%20and%20Code%20Quality/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/lint.yml)
[![Code Coverage](https://codecov.io/gh/MeridianAlgo/Cryptvault/branch/main/graph/badge.svg)](https://codecov.io/gh/MeridianAlgo/Cryptvault)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **IMPORTANT DISCLAIMER**: This software is for educational and research purposes only. It is NOT financial advice and should NOT be used for actual trading or investment decisions. You are solely responsible for your investment decisions and any financial losses.

## Overview

CryptVault is an advanced cryptocurrency and stock analysis platform featuring machine learning-powered predictions, comprehensive technical analysis, and sophisticated pattern detection capabilities.

### Key Features

- **Advanced Pattern Detection**: 15+ chart patterns including Head & Shoulders, Double Top/Bottom, Triangles, Wedges, Flags, and Cup & Handle
- **Machine Learning Ensemble**: Combines multiple ML models (Random Forest, Gradient Boosting, SVM, Linear Regression, ARIMA) for robust predictions
- **Technical Indicators**: RSI, MACD, Moving Averages, Bollinger Bands, and volume analysis
- **Professional Charting**: Clean candlestick charts with pattern overlays and technical indicators
- **Automated Training**: Models retrain hourly with fresh market data
- **Multi-Asset Support**: Analyze cryptocurrencies and stocks with unified interface

### What's New in v5.0.0

- Enhanced ML ensemble with 10+ optimized models (Random Forest, XGBoost, LightGBM, CatBoost)
- Advanced models: Bayesian Ridge, Quantile Regression, Stacked Ensembles
- Professional CI/CD with automated testing and linting workflows
- Automated GitHub issue creation on workflow failures
- Comprehensive code quality checks (Black, isort, Flake8, Pylint, MyPy, Bandit)
- Code of Conduct and improved documentation
- Optimized hyperparameters for all ML models
- Better prediction accuracy and confidence scoring

**Developed by MeridianAlgo** - Algorithmic trading research and development.

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Analyze Bitcoin with chart
python cryptvault_cli.py BTC 60 1d

# Save chart to file
python cryptvault_cli.py ETH 120 1d --save-chart eth_chart.png

# Text-only analysis (no chart)
python cryptvault_cli.py SOL 90 1d --no-chart
```

---

## Features

### Pattern Detection

**Reversal Patterns**
- Head and Shoulders / Inverse Head and Shoulders
- Double Top / Double Bottom
- Triple Top / Triple Bottom
- Rounding Top / Rounding Bottom

**Continuation Patterns**
- Ascending Triangle / Descending Triangle / Symmetrical Triangle
- Rising Wedge / Falling Wedge
- Bull Flag / Bear Flag
- Pennants and Channels

**Special Patterns**
- Cup and Handle
- Gap Patterns (Up/Down)
- Support and Resistance Levels

### Machine Learning Ensemble

The platform combines multiple ML algorithms for robust predictions:

- **Random Forest**: Tree-based ensemble learning
- **Gradient Boosting**: Sequential model optimization
- **Support Vector Machines**: Non-linear regression
- **Linear Models**: Ridge, Lasso, and ElasticNet regression
- **ARIMA**: Time series forecasting
- **XGBoost/LightGBM**: Advanced gradient boosting (optional)

Each model contributes to the final prediction with weighted voting based on historical accuracy.

### Technical Indicators

- **Trend**: Moving Averages (SMA, EMA, WMA), MACD
- **Momentum**: RSI, Stochastic Oscillator, CCI, ROC
- **Volatility**: Bollinger Bands, ATR, Standard Deviation
- **Volume**: OBV, VWAP, Accumulation/Distribution Line

---

## Usage Examples

### Cryptocurrency Analysis

```bash
# Quick analysis
python cryptvault_cli.py BTC 60 1d

# Extended analysis with chart export
python cryptvault_cli.py ETH 90 1d --save-chart ethereum_analysis.png

# Multiple timeframes
python cryptvault_cli.py SOL 30 4h  # 30 days, 4-hour intervals
```

### Stock Analysis

```bash
# Analyze stocks
python cryptvault_cli.py AAPL 60 1d
python cryptvault_cli.py TSLA 90 1d --save-chart tesla.png

# Verbose output
python cryptvault_cli.py GOOGL 60 1d --verbose
```

### Advanced Features

```bash
# Portfolio analysis
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10 ADA:1000

# Multi-asset comparison
python cryptvault_cli.py --compare BTC ETH SOL

# Interactive mode
python cryptvault_cli.py --interactive

# Check system status
python cryptvault_cli.py --status
```

---

## Command Reference

### Basic Syntax

```bash
python cryptvault_cli.py SYMBOL [DAYS] [INTERVAL] [OPTIONS]
```

### Options

- `--no-chart`: Text-only output without chart display
- `--save-chart FILE`: Save chart to specified file
- `--verbose`: Detailed output with all indicators
- `--demo`: Run interactive demonstration
- `--version`: Show version information
- `--help`: Display help message

### Advanced Commands

- `--portfolio ASSET:AMOUNT ...`: Analyze portfolio composition
- `--compare SYMBOL1 SYMBOL2 ...`: Compare multiple assets
- `--interactive`: Enter interactive analysis mode
- `--status`: Check API and system status
- `--accuracy`: Display prediction accuracy metrics

---

## Project Structure

```
CryptVault/
├── cryptvault/              # Core package
│   ├── core/                # Analysis engine
│   ├── patterns/            # Pattern detection
│   ├── indicators/          # Technical indicators
│   ├── ml/                  # Machine learning models
│   ├── data/                # Data management
│   ├── visualization/       # Chart generation
│   ├── portfolio/           # Portfolio analysis
│   ├── cli/                 # Command-line interface
│   ├── security/            # Security utilities
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── config/                  # Configuration files
├── requirements/            # Dependency specifications
├── cryptvault_cli.py        # Main CLI entry point
├── setup.py                 # Package setup
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

---

## System Requirements

### Minimum Requirements

- Python 3.9 or higher
- 4GB RAM
- 2GB disk space
- Internet connection for data fetching

### Recommended Requirements

- Python 3.11 or higher
- 8GB RAM
- 5GB disk space
- Stable internet connection

### Supported Platforms

- Windows 10/11
- Ubuntu 20.04+
- macOS 10.15+ (including Apple Silicon)

---

## Performance Metrics

- **Pattern Detection**: Sub-2-second analysis for 60 days of data
- **ML Predictions**: Sub-3-second prediction generation
- **Model Accuracy**: 85%+ ensemble accuracy
- **Memory Usage**: Under 500MB typical operation
- **Feature Engineering**: 40+ technical indicators computed

---

## Documentation

### User Documentation

- [Quick Start Guide](docs/QUICK_GUIDE.md)
- [CLI Guide](docs/CLI_VS_CORE.md)
- [Interactive Charts](docs/INTERACTIVE_CHART_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

### Technical Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Changelog](docs/CHANGELOG.md)
- [Performance Guide](docs/PERFORMANCE.md)

### Security and Compliance

- [Security Policy](docs/SECURITY.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

---

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=cryptvault --cov-report=html

# Specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code
black cryptvault/ cryptvault_cli.py

# Sort imports
isort cryptvault/ cryptvault_cli.py

# Lint code
flake8 cryptvault/
pylint cryptvault/

# Type checking
mypy cryptvault/

# Security audit
bandit -r cryptvault/
```

---

## Contributing

We welcome contributions from the community. Please read our [Contributing Guide](docs/CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -r requirements/dev.txt`
4. Make your changes
5. Run tests and linting
6. Submit a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Credits

Built with contributions from:

- **MeridianAlgo Team**: Core development and algorithmic trading expertise
- **scikit-learn**: Machine learning framework
- **yfinance**: Market data access
- **CCXT**: Cryptocurrency exchange integration
- **NumPy, pandas, SciPy**: Scientific computing
- **Matplotlib**: Data visualization
- **XGBoost, LightGBM**: Advanced ML algorithms

For complete credits, see [CREDITS.md](docs/CREDITS.md).

---

## Disclaimers

### Educational and Research Use Only

This software is strictly for educational and research purposes.

- **NOT FINANCIAL ADVICE**: Does not provide financial, investment, or trading advice
- **NOT FOR TRADING**: Do not use for actual investment or trading decisions
- **RESEARCH TOOL**: Machine learning research and pattern recognition exploration
- **NO GUARANTEES**: Past performance does not guarantee future results

### About MeridianAlgo

MeridianAlgo is a nonprofit research organization focused on machine learning research, open-source financial technology tools, and educational resources. We are NOT a licensed financial advisor, broker, or investment firm.

### Investment Risk Warning

Cryptocurrency and stock trading involves substantial risk of loss. You may lose some or all of your invested capital. Market predictions are inherently uncertain. Consult a licensed financial advisor before making investment decisions.

### Appropriate Uses

**Appropriate for:**
- Learning machine learning algorithms
- Studying technical analysis and market patterns
- Academic research and coursework
- Developing and testing prediction models
- Pattern recognition research

**NOT appropriate for:**
- Making actual investment decisions
- Trading with real money
- Providing financial advice to others
- Commercial trading operations

For complete terms, see [LICENSE](LICENSE) and [PRIVACY.md](docs/PRIVACY.md).

---

## Support

### Getting Help

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/MeridianAlgo/Cryptvault/issues)
- **Email**: support@meridianalgo.com

### Reporting Bugs

Use the [issue tracker](https://github.com/MeridianAlgo/Cryptvault/issues) and include:
- Python version
- Operating system
- Error messages
- Steps to reproduce

---

## Frequently Asked Questions

**Q: How accurate are the predictions?**
A: Ensemble models achieve 85%+ accuracy. Individual predictions include confidence scores.

**Q: Do I need API keys?**
A: No, CryptVault uses free data sources by default. API keys are optional.

**Q: Can I use custom data?**
A: Yes, the Python API supports custom data sources and formats.

**Q: Does it work offline?**
A: Data fetching requires internet, but analysis works with cached data.

**Q: What patterns are detected?**
A: 15+ patterns including reversal, continuation, and special patterns.

**Q: Can I analyze stocks and crypto together?**
A: Yes, both asset types are supported in the same analysis.

---

**Version**: 5.0.0  
**Last Updated**: January 2026  
**Maintained by**: MeridianAlgo
