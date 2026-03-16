# CryptVault - AI-Powered Cryptocurrency Analysis Platform

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-6.0.0-brightgreen.svg)](https://github.com/MeridianAlgo/Cryptvault/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/MeridianAlgo/Cryptvault/workflows/Tests/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/tests.yml)
[![Lint](https://github.com/MeridianAlgo/Cryptvault/workflows/Lint%20and%20Code%20Quality/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/lint.yml)
[![Code Coverage](https://codecov.io/gh/MeridianAlgo/Cryptvault/branch/main/graph/badge.svg)](https://codecov.io/gh/MeridianAlgo/Cryptvault)


> **IMPORTANT DISCLAIMER**: This software is for educational and research purposes only. It is NOT financial advice and should NOT be used for actual trading or investment decisions. You are solely responsible for your investment decisions and any financial losses.

## Overview

CryptVault is an advanced cryptocurrency and stock analysis platform featuring a native desktop GUI, production-grade machine learning predictions, comprehensive technical analysis, and sophisticated pattern detection.

### Key Features

- **Native Desktop App**: Dark-themed trading terminal with candlestick charts, pattern overlays, and ML predictions
- **Pattern Detection**: 50+ patterns across 7 categories — candlestick, reversal, continuation, harmonic, and divergence
- **Actual Pattern Drawing**: Reversal and continuation patterns are drawn as geometric shapes on the chart (necklines, trendlines, pivot connections)
- **Production ML System**: Ensemble predictor with stacking, 67+ engineered features, and validation-based weighting
- **Reinforcement Learning**: RL agents (DQN, PPO, Transformer) for trading research
- **Technical Indicators**: Bollinger Bands, RSI, Volume — cleanly rendered without clutter
- **Multi-Asset Support**: Cryptocurrencies and stocks via Yahoo Finance

### ML Performance (Real Market Data)

- **Average MAPE**: 1.6-2.4% across major cryptocurrencies
- **Direction Accuracy**: 100% on tested symbols
- **Within 2% Accuracy**: 80-100% of predictions
- **R2 Score**: 0.50-0.81

Tested on BTC, ETH, SOL, BNB with 120 days of historical data.

### What Changed in v6.0.0

- **Desktop App Overhaul**: Removed cluttered moving averages, removed unnecessary real-time streaming tab
- **Actual Pattern Drawing**: Double Tops/Bottoms, Head & Shoulders, Triangles, and Wedges now draw actual geometric shapes (trendlines, necklines, pivot connections) on the chart instead of just markers
- **Fixed Pattern Detection**: Double Bottom strength calculation bug fixed; all chart patterns now store key point coordinates in `extra` field
- **Cleaner Analysis**: Analysis panel always visible alongside chart in a split pane
- **Simplified Navigation**: Chart and Analysis only — no unused real-time tab
- **Docs**: Added DESKTOP_APP.md and PATTERNS.md

**Developed by MeridianAlgo** - Algorithmic trading research and development.

---

## Quick Start

### Installation

```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
```

### Desktop App

```bash
python launch_desktop.py
```

### CLI

```bash
# Analyze Bitcoin with chart
python cryptvault_cli.py BTC 60 1d

# Save chart to file
python cryptvault_cli.py ETH 120 1d --save-chart eth_chart.png

# Text-only analysis
python cryptvault_cli.py SOL 90 1d --no-chart
```

---

## Desktop Application

The desktop app provides a full trading terminal experience.

### Layout

```
+------------------------------------------------------------------+
| CryptVault v6.0  [Symbol: BTC-USD]  [Analyze]  1D 5D 1M 3M ...  |
+----------+--------------------------------------+------------------+
| Chart    |                                      |  ML Prediction   |
| Analysis |     Candlestick Chart                |  ────────────    |
|          |     Bollinger Bands                  |  Detected        |
| ───────  |     Pattern shapes (drawn)           |  Patterns        |
| LAST     |     Volume                           |  (scrollable)    |
| ANALYSIS |     RSI                              |                  |
+----------+--------------------------------------+------------------+
| Status bar                                                        |
+------------------------------------------------------------------+
```

### Pattern Visualization

Patterns are rendered as actual geometric shapes:

| Pattern | Drawn As |
|---------|----------|
| Double Top / Bottom | Lines connecting peaks/troughs + dashed neckline |
| Head & Shoulders | LS-Head-RS connection + dashed neckline |
| Triple Top / Bottom | Lines connecting all three pivot points |
| Triangles (Sym/Asc/Desc) | Upper and lower fitted trendlines |
| Rising / Falling Wedge | Upper and lower fitted trendlines |
| All patterns with target | Dotted horizontal target price line |
| Candlestick patterns | Triangle marker (^ bullish, v bearish) |

See [Desktop App Documentation](docs/DESKTOP_APP.md) for full details.

---

## Features

### Pattern Detection

50+ patterns across 7 categories. See [Pattern Reference](docs/PATTERNS.md).

**Reversal Patterns**
- Head and Shoulders / Inverse Head and Shoulders
- Double Top / Double Bottom
- Triple Top / Triple Bottom
- Rising Wedge / Falling Wedge

**Continuation Patterns**
- Ascending Triangle / Descending Triangle / Symmetrical Triangle
- Bull Flag / Bear Flag / Pennants
- Cup and Handle

**Candlestick Patterns**
- Doji (Standard, Gravestone, Dragonfly)
- Hammer, Hanging Man, Inverted Hammer, Shooting Star
- Engulfing, Harami, Piercing Line, Dark Cloud Cover
- Morning Star, Evening Star, Three White Soldiers, Three Black Crows

**Harmonic Patterns**
- Gartley, Butterfly, Bat, Crab, Shark, Cypher

**Divergence**
- RSI Bullish/Bearish Divergence
- MACD Bullish/Bearish Divergence

### Machine Learning Ensemble

- **Random Forest**: Tree-based ensemble learning
- **Gradient Boosting**: Sequential model optimization
- **Support Vector Machines**: Non-linear regression
- **Linear Models**: Ridge, Lasso, ElasticNet
- **ARIMA**: Time series forecasting
- **XGBoost/LightGBM**: Advanced gradient boosting (optional)

Each model is weighted by historical validation accuracy.

### Reinforcement Learning

State-of-the-art RL agents for trading research:
- **DQN**: Deep Q-Network with Rainbow improvements (dueling, noisy nets, prioritized replay)
- **PPO**: Proximal Policy Optimization with GAE
- **Transformer**: Multi-head attention for sequential decisions

See [RL Documentation](cryptvault/rl/README.md) for usage.

---

## Usage Examples

### Cryptocurrency Analysis

```bash
python cryptvault_cli.py BTC 60 1d
python cryptvault_cli.py ETH 90 1d --save-chart ethereum_analysis.png
python cryptvault_cli.py SOL 30 4h
```

### Stock Analysis

```bash
python cryptvault_cli.py AAPL 60 1d
python cryptvault_cli.py TSLA 90 1d --save-chart tesla.png
python cryptvault_cli.py GOOGL 60 1d --verbose
```

### Advanced

```bash
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10
python cryptvault_cli.py --compare BTC ETH SOL
python cryptvault_cli.py --interactive
python cryptvault_cli.py --status
```

---

## Command Reference

```bash
python cryptvault_cli.py SYMBOL [DAYS] [INTERVAL] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--no-chart` | Text-only output |
| `--save-chart FILE` | Save chart image |
| `--verbose` | Detailed output |
| `--demo` | Run demonstration |
| `--desktop` | Launch desktop app |
| `--version` | Show version |
| `--help` | Show help |
| `--portfolio ASSET:AMT ...` | Portfolio analysis |
| `--compare SYM1 SYM2 ...` | Compare assets |
| `--interactive` | Interactive REPL |
| `--status` | Check API status |

---

## Project Structure

```
CryptVault/
    cryptvault/
        desktop/             Native desktop GUI
            app.py
            main_window.py
            theme.py
            panels/
                chart_panel.py
                analysis_panel.py
        patterns/            Pattern detection
            comprehensive.py (50+ patterns, 7 categories)
        ml/                  Machine learning models
        rl/                  Reinforcement learning agents
        data/                Data fetching and management
        visualization/       Chart generation
        portfolio/           Portfolio analysis
    docs/
        DESKTOP_APP.md       Desktop app guide
        PATTERNS.md          Pattern detection reference
        ARCHITECTURE.md
        API_REFERENCE.md
        TROUBLESHOOTING.md
    tests/
    cryptvault_cli.py        CLI entry point
    launch_desktop.py        Desktop launcher
    requirements.txt
```

---

## System Requirements

### Minimum

- Python 3.9+
- 4 GB RAM
- 2 GB disk space
- Internet connection (data fetching)

### Recommended

- Python 3.11+
- 8 GB RAM
- 5 GB disk space

### Platforms

- Windows 10/11
- Ubuntu 20.04+
- macOS 10.15+ (including Apple Silicon)

---

## Development

### Running Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=cryptvault --cov-report=html
```

### Code Quality

```bash
black cryptvault/ cryptvault_cli.py
isort cryptvault/ cryptvault_cli.py
flake8 cryptvault/
mypy cryptvault/
bandit -r cryptvault/
```

---

## Documentation

- [Desktop App Guide](docs/DESKTOP_APP.md)
- [Pattern Reference](docs/PATTERNS.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Changelog](docs/CHANGELOG.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Security Policy](docs/SECURITY.md)

---

## Contributing

Read [CONTRIBUTING.md](docs/CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before submitting pull requests.

1. Fork the repository
2. Create a feature branch
3. Install dev dependencies: `pip install -r requirements.txt`
4. Make your changes with tests
5. Run tests and linting
6. Submit a pull request

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Credits

- **MeridianAlgo Team**: Core development
- **scikit-learn**: Machine learning
- **yfinance**: Market data
- **NumPy, pandas, SciPy**: Scientific computing
- **Matplotlib**: Visualization
- **XGBoost, LightGBM**: Gradient boosting

---

## Disclaimers

This software is strictly for educational and research purposes.

- **NOT FINANCIAL ADVICE**: Does not provide investment or trading advice
- **NOT FOR TRADING**: Do not use for actual investment decisions
- **NO GUARANTEES**: Past performance does not guarantee future results

MeridianAlgo is a nonprofit research organization focused on ML research and open-source financial technology. We are not a licensed financial advisor, broker, or investment firm.

---

**Version**: 6.0.0
**Last Updated**: March 2026
**Maintained by**: MeridianAlgo
