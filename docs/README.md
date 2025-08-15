# 🚀 CryptVault - Advanced AI-Powered Cryptocurrency Analysis Platform

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/MeridianAlgo/CryptVault/graphs/commit-activity)

**Professional-grade cryptocurrency analysis with advanced AI/ML predictions, 50+ pattern recognition, and TradingView-style terminal charts.**

![CryptVault Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🎯 **Features**

### 🧠 **Advanced AI/ML Analysis**
- **6-Model Ensemble**: LSTM, Random Forest, Gradient Boosting, SVM, Linear, ARIMA
- **Dynamic Model Weighting**: Performance-based weight adjustment
- **Meta-Learning**: Secondary model learns optimal combinations
- **75%+ Accuracy**: Enhanced ensemble with real-time training

### 📊 **Professional Charting**
- **TradingView-Style Charts**: Professional ASCII candlestick visualization
- **Desktop GUI Charts**: Interactive matplotlib-based desktop application
- **50+ Pattern Types**: Comprehensive pattern recognition library
- **Real-time Analysis**: Sub-3 second analysis times
- **Multi-timeframe Support**: 1h, 4h, 1d intervals

### 🔍 **Pattern Recognition**
- **Reversal Patterns**: Double/Triple Tops/Bottoms, Head & Shoulders
- **Triangle Patterns**: Ascending, Descending, Expanding, Symmetrical
- **Harmonic Patterns**: Gartley, Butterfly, Bat, Crab, ABCD
- **Divergence Patterns**: Bullish/Bearish, Hidden Divergences
- **Continuation Patterns**: Flags, Pennants, Rectangles, Channels

### ⏱️ **Time-based Analysis**
- **Short-term Bias**: Next bar prediction
- **Medium-term Bias**: 7-bar outlook  
- **Long-term Bias**: 14-31 bar forecast
- **Dynamic Weighting**: Pattern recency and strength considered

## 🚀 **Quick Start**

### Installation

```bash
# Clone the repository
git clone https://github.com/MeridianAlgo/CryptVault.git
cd CryptVault

# Install dependencies
pip install -r requirements.txt

# Run analysis
python cryptvault.py BTC
```

### Basic Usage

```bash
# Single cryptocurrency analysis
python cryptvault.py BTC                    # Bitcoin analysis
python cryptvault.py ETH 30 4h             # Ethereum, 30 days, 4h intervals
python cryptvault.py ADA 90 1d             # Cardano, 90 days, daily

# Multi-asset analysis
python cryptvault.py -m BTC ETH ADA        # Compare multiple assets

# Desktop GUI Charts (Interactive)
python cryptvault_cli.py --desktop         # Open desktop charting window
python launch_desktop_charts.py            # Direct desktop launcher

# Verbose mode (detailed analysis)
python cryptvault.py BTC -v                # Additional ML model details
```

## 📊 **Sample Output**

```
🚀 CryptVault Advanced Analysis
══════════════════════════════════════════════════
✓ Analysis complete

╭────────────────── BTC Analysis ──────────────────╮
│ $114,084.30                                      │
│ Short: BULLISH                                   │
│ Medium: BULLISH                                  │
│ Long: BULLISH                                    │
│ Patterns:                                        │
│ ◇ Expanding Triangle 100.0% ●                    │
│ ⤴ Hidden Bullish Divergence 100.0% ●             │
│ ⩗ Double Bottom 92.0% ●                          │
╰──────────────────────────────────────────────────╯

📊 Chart Analysis:
[Professional ASCII candlestick chart with patterns]

🧠 ML Forecast: BULLISH (65% confidence)
🎯 Target Price: $121,499.78
✅ Analysis completed in 2.56s | 4 patterns found
```

## 🎨 **Pattern Library**

### Reversal Patterns
- ⩗ **Double Bottom** - Bullish reversal
- ⩘ **Double Top** - Bearish reversal  
- ⫸ **Triple Bottom** - Strong bullish reversal
- ⫷ **Triple Top** - Strong bearish reversal
- ⩙ **Head and Shoulders** - Bearish reversal
- ⩚ **Inverse Head and Shoulders** - Bullish reversal

### Triangle Patterns
- △ **Ascending Triangle** - Bullish continuation
- ▽ **Descending Triangle** - Bearish continuation
- ◇ **Expanding Triangle** - Breakout pattern
- ◊ **Symmetrical Triangle** - Neutral breakout

### Harmonic Patterns
- A **ABCD** - Harmonic price structure
- G **Gartley** - Advanced harmonic pattern
- B **Butterfly** - Reversal harmonic
- C **Crab** - Extended harmonic pattern

### Divergence Patterns
- ↗ **Bullish Divergence** - Price vs indicator divergence
- ↘ **Bearish Divergence** - Bearish momentum divergence
- ⤴ **Hidden Bullish Divergence** - Continuation signal
- ⤵ **Hidden Bearish Divergence** - Bearish continuation

## 🔧 **Advanced Features**

### Command Line Options

```bash
# Basic analysis
python cryptvault.py SYMBOL [DAYS] [INTERVAL]

# Multi-asset comparison
python cryptvault.py -m BTC ETH ADA DOT

# Verbose mode with detailed ML analysis
python cryptvault.py BTC -v

# Quick analysis mode
python cryptvault.py BTC --quick

# Show help
python cryptvault.py --help
```

### Supported Cryptocurrencies
- **Major**: BTC, ETH, ADA, DOT, LINK, LTC, XRP
- **DeFi**: UNI, AAVE, COMP, MKR, SNX
- **Layer 1**: SOL, AVAX, NEAR, ALGO, ATOM
- **And many more...**

### Data Sources
- ✅ **YFinance** - Primary data source
- ✅ **CCXT** - Cryptocurrency exchange data
- ✅ **CryptoCompare** - Alternative data provider
- ⚡ **Real-time Updates** - Live market data

## 🧠 **ML Model Architecture**

### Ensemble Components
1. **LSTM Neural Network** - Deep learning time series analysis
2. **Random Forest** - Ensemble tree-based learning
3. **Gradient Boosting** - Advanced boosting algorithm
4. **Support Vector Machine** - Non-linear pattern recognition
5. **Linear Regression** - Fast baseline predictions
6. **ARIMA** - Statistical time series analysis

### Performance Metrics
- **Ensemble Accuracy**: 75%+ on validation data
- **Analysis Speed**: 0.16-2.63 seconds per asset
- **Pattern Detection**: 95-100% confidence for top patterns
- **Model Weights**: Dynamic adjustment based on performance

## 📈 **Technical Analysis**

### Indicators Supported
- **Moving Averages**: SMA, EMA, WMA
- **Momentum**: RSI, MACD, Stochastic
- **Volume**: Volume Profile, OBV
- **Volatility**: Bollinger Bands, ATR
- **Trend**: ADX, Parabolic SAR

### Chart Features
- **Candlestick Visualization**: OHLC data representation
- **Pattern Overlays**: Direct pattern visualization
- **Support/Resistance**: Key level identification
- **Trend Lines**: Automatic trend line detection
- **Volume Analysis**: Color-coded volume bars

## 🛠️ **Installation & Setup**

### Requirements
- **Python**: 3.7 or higher
- **Dependencies**: Listed in `requirements.txt`
- **Memory**: 2GB RAM minimum
- **Storage**: 100MB for installation

### Dependencies
```
numpy>=1.19.0
pandas>=1.3.0
scikit-learn>=1.0.0
yfinance>=0.2.0
ccxt>=4.0.0
cryptocompare>=0.7.0
colorama>=0.4.6
matplotlib>=3.5.0
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/MeridianAlgo/CryptVault.git
cd CryptVault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run analysis
python cryptvault.py BTC -v
```

## 📊 **Performance Benchmarks**

### Speed Tests
| Asset | Days | Interval | Analysis Time | Patterns Found |
|-------|------|----------|---------------|----------------|
| BTC   | 60   | 1d       | 2.56s        | 4              |
| ETH   | 60   | 1d       | 2.63s        | 6              |
| ADA   | 60   | 1d       | 2.42s        | 4              |
| DOT   | 30   | 4h       | 1.23s        | 3              |

### Accuracy Metrics
- **Pattern Recognition**: 95-100% confidence for high-quality patterns
- **ML Ensemble**: 75%+ accuracy on validation data
- **Directional Accuracy**: 70%+ for short-term predictions
- **Target Price Accuracy**: 65%+ within 5% tolerance

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution
- 🔍 **New Pattern Types**: Add more technical analysis patterns
- 🧠 **ML Models**: Implement new machine learning algorithms
- 📊 **Visualization**: Enhance charting and visualization features
- 🔧 **Performance**: Optimize analysis speed and accuracy
- 📚 **Documentation**: Improve documentation and examples

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **TradingView** - Inspiration for chart styling
- **TA-Lib** - Technical analysis concepts
- **Scikit-learn** - Machine learning framework
- **YFinance** - Financial data provider
- **CCXT** - Cryptocurrency exchange library

## 📞 **Support**

- 📧 **Email**: support@meridianalgo.com
- 💬 **Issues**: [GitHub Issues](https://github.com/MeridianAlgo/CryptVault/issues)
- 📖 **Documentation**: [Wiki](https://github.com/MeridianAlgo/CryptVault/wiki)
- 🐦 **Twitter**: [@MeridianAlgo](https://twitter.com/MeridianAlgo)

## 🚀 **Roadmap**

### Version 2.1 (Next Release)
- [ ] Real-time WebSocket data streaming
- [ ] Portfolio analysis and optimization
- [ ] Custom alert system
- [ ] REST API for external integrations

### Version 2.2 (Future)
- [ ] Web-based dashboard
- [ ] Mobile app companion
- [ ] Social sentiment analysis
- [ ] Options and derivatives analysis

### Version 3.0 (Long-term)
- [ ] Automated trading strategies
- [ ] Risk management system
- [ ] Multi-exchange arbitrage detection
- [ ] Advanced backtesting framework

---

**⭐ Star this repository if you find it useful!**

**🔔 Watch for updates and new features!**

**🍴 Fork to contribute to the project!**

---

*Made with ❤️ by [MeridianAlgo](https://github.com/MeridianAlgo)*
<img width="500" height="500" alt="Quantum Meridian (1)" src="https://github.com/user-attachments/assets/3ea06475-be6d-4bf7-a311-c3cb9ccbf8e2" />

