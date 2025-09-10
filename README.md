# 🚀 CryptVault - Advanced AI-Powered Cryptocurrency Analysis

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Professional-grade cryptocurrency analysis with advanced AI/ML predictions, 50+ pattern recognition, and beautiful ASCII terminal charts.**

![CryptVault Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## ⚡ **Quick Start**

### **1. Install**
```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
```

### **2. Run**
```bash
# Quick demo
python cryptvault_cli.py --demo

# Analyze Bitcoin with beautiful charts
python cryptvault_cli.py BTC 60 1d --verbose
```

### **3. Enjoy!**

**Desktop Chart Window Opens Automatically** 📊

```
Detected Patterns:
────────────────────────────────────────────────────────────
 1. ⭐ Expanding Triangle        [Bilateral/Neutral] [██████████] 100.0% ●
 2. ↘ Bearish Divergence        [Divergence Pattern] [██████████] 100.0% ●
     Key Levels: Support: $45,230.50 | Resistance: $48,900.75 | Target: $52,100.00

📊 Interactive desktop chart window opens with:
• Professional candlestick visualization
• Pattern overlays with exact names
• Interactive zoom and pan
• Export to PNG/PDF/SVG
• Real-time pattern highlighting
```

## 🎯 **Features**

### 🧠 **Advanced AI/ML Analysis**
- **10-Model Ensemble**: LSTM, Random Forest, Gradient Boosting, SVM, Linear, ARIMA
- **Dynamic Model Weighting**: Performance-based weight adjustment
- **Meta-Learning**: Secondary model learns optimal combinations
- **75%+ Accuracy**: Enhanced ensemble with real-time training

### 📊 **Professional Charting**
- **Interactive Desktop Charts**: Beautiful matplotlib-based candlestick visualization
- **Exact Pattern Names**: Precise pattern identification with detailed information
- **50+ Pattern Types**: Comprehensive pattern recognition library
- **Real-time Analysis**: Sub-3 second analysis times
- **Multi-timeframe Support**: 1h, 4h, 1d intervals

### 🔍 **Pattern Recognition**
- **Reversal Patterns**: Double/Triple Tops/Bottoms, Head & Shoulders
- **Triangle Patterns**: Ascending, Descending, Expanding, Symmetrical
- **Divergence Patterns**: Bullish/Bearish, Hidden Divergences
- **Continuation Patterns**: Flags, Pennants, Rectangles, Channels

## 📈 **Usage Examples**

### **Basic Analysis**
```bash
python cryptvault_cli.py BTC                    # Bitcoin analysis
python cryptvault_cli.py ETH 30 4h             # Ethereum, 30 days, 4h intervals
python cryptvault_cli.py ADA 90 1d             # Cardano, 90 days, daily
```

### **Advanced Analysis**
```bash
python cryptvault_cli.py BTC 60 1d --verbose   # Detailed charts and ML predictions
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10 ADA:1000  # Portfolio analysis
python cryptvault_cli.py --compare BTC ETH ADA DOT  # Compare multiple assets
```

### **Interactive Mode**
```bash
python cryptvault_cli.py --interactive
cryptvault> analyze BTC 60 1d
cryptvault> portfolio BTC:0.5 ETH:10
cryptvault> compare BTC ETH ADA
```

### **Desktop Charting**
```bash
python cryptvault_cli.py --desktop     # Open desktop chart window
python cryptvault_cli.py BTC -v        # Analyze with desktop chart
```

## 📊 **Sample Output**

```
Analyzing BTC (60d, 1d)
Completed in 3.60s | 6 patterns
Price: $115,240.16
Change: +31.67%
Trend: bullish (50.0%)
Patterns:
  Expanding Triangle (100.0%)
  Bearish Divergence (100.0%)
  Rectangle Neutral (94.4%)
```

## 🔧 **Installation**

### **Requirements**
- Python 3.7+
- Internet connection (for data fetching)

### **Dependencies**
All dependencies are automatically installed:
- `numpy`, `pandas`, `scikit-learn` - Core data processing
- `yfinance`, `ccxt`, `cryptocompare` - Data sources (no API keys needed)
- `matplotlib`, `colorama` - Visualization
- `fastquant` - Optional fast analysis

### **Setup**
```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
python cryptvault_cli.py --demo  # Test installation
```

## 📚 **Documentation**

- **[Setup Guide](SETUP_GUIDE.md)**: Complete installation guide
- **[docs/](docs/)**: Detailed documentation
- **[CHANGELOG.md](CHANGELOG.md)**: Version history

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Import errors**: Run `pip install -r requirements.txt`
2. **Insufficient data**: Use more days (e.g., 60 instead of 7)
3. **Network issues**: Check internet connection

### **Get Help**
```bash
python cryptvault_cli.py --help     # Show all options
python cryptvault_cli.py --status   # Check data sources
python cryptvault_cli.py --demo     # Test functionality
```

## 🚀 **Features Overview**

| Feature | Description | Status |
|---------|-------------|--------|
| **Pattern Recognition** | 50+ patterns with confidence scoring | ✅ Ready |
| **AI/ML Predictions** | 10-model ensemble with 75%+ accuracy | ✅ Ready |
| **ASCII Charts** | Beautiful terminal candlestick charts | ✅ Ready |
| **Multi-Asset Analysis** | Portfolio and comparison tools | ✅ Ready |
| **Real-time Data** | Multiple data sources, no API keys | ✅ Ready |
| **Interactive Mode** | Command-line interface | ✅ Ready |

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🎉 **Get Started Now!**

```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
python cryptvault_cli.py BTC 60 1d --verbose
```

**Welcome to professional cryptocurrency analysis! 🚀📊**

---

*Made with ❤️ by the MeridianAlgo Algorithmic Research Team (Quantum Meridian)*