# 🚀 CryptVault Setup Guide

**Complete installation guide for new users to get CryptVault running from scratch.**

## 📋 **Prerequisites**

- **Python 3.7+** (Recommended: Python 3.9 or higher)
- **Git** (for cloning the repository)
- **Internet connection** (for downloading data)

## 🔧 **Installation Steps**

### **1. Clone the Repository**
```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
```

### **2. Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt
```

### **3. Verify Installation**
```bash
# Test the installation
python cryptvault_cli.py --demo
```

You should see output like:
```
Found:
  BTC: Bitcoin
  BCH: Bitcoin Cash
Supported: BTC, ETH, ADA, DOT, LINK, LTC, XRP, BCH, BNB, SOL
BTC: $115,203.14
```

## 🚀 **Quick Start**

### **Basic Analysis**
```bash
# Analyze Bitcoin with default settings (30 days, daily)
python cryptvault_cli.py BTC

# Analyze with custom timeframe
python cryptvault_cli.py BTC 60 1d

# Get detailed charts and analysis
python cryptvault_cli.py BTC 60 1d --verbose
```

### **Example Output**
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

[Beautiful ASCII candlestick chart with pattern overlays]
```

## 📊 **Available Commands**

### **Analysis Commands**
```bash
# Basic analysis
python cryptvault_cli.py BTC                    # Bitcoin analysis
python cryptvault_cli.py ETH 30 4h             # Ethereum, 30 days, 4h intervals
python cryptvault_cli.py ADA 90 1d             # Cardano, 90 days, daily

# Detailed analysis with charts
python cryptvault_cli.py BTC 60 1d --verbose   # Full analysis with ASCII charts

# Portfolio analysis
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10 ADA:1000

# Compare multiple assets
python cryptvault_cli.py --compare BTC ETH ADA DOT
```

### **Utility Commands**
```bash
# Show help
python cryptvault_cli.py --help

# Run demo
python cryptvault_cli.py --demo

# Check data source status
python cryptvault_cli.py --status

# Interactive mode
python cryptvault_cli.py --interactive
```

## 🎯 **Features**

### **📈 Pattern Recognition**
- **50+ Pattern Types**: Triangles, Rectangles, Divergences, Reversals
- **ASCII Chart Visualization**: Beautiful terminal-based candlestick charts
- **Pattern Overlays**: Visual pattern markers on charts
- **Confidence Scoring**: Reliability assessment for each pattern

### **🧠 AI/ML Predictions**
- **10-Model Ensemble**: LSTM, Random Forest, Gradient Boosting, SVM, etc.
- **Trend Forecasting**: 7-day trend predictions
- **Price Targets**: ML-generated price predictions
- **Confidence Levels**: Prediction reliability scores

### **📊 Technical Analysis**
- **Multiple Timeframes**: 1h, 4h, 1d intervals
- **Volume Analysis**: Trading volume insights
- **Support/Resistance**: Key price levels
- **Trend Analysis**: Market direction assessment

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Import Errors**
```bash
ModuleNotFoundError: No module named 'cryptvault.data'
```
**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

#### **2. Insufficient Data**
```bash
❌ Analysis failed: Insufficient data points. Need at least 50, got 14
```
**Solution**: Use more days of data:
```bash
python cryptvault_cli.py BTC 60 1d  # Use 60 days instead of 7
```

#### **3. Network Issues**
```bash
Failed to fetch data for BTC
```
**Solution**: Check internet connection and try again. The system uses multiple data sources (yfinance, ccxt, cryptocompare) for reliability.

### **Performance Tips**

1. **Use appropriate timeframes**:
   - For quick analysis: `python cryptvault_cli.py BTC 30 1d`
   - For detailed analysis: `python cryptvault_cli.py BTC 90 1d --verbose`

2. **Pattern detection requires sufficient data**:
   - Minimum: 50 data points
   - Recommended: 60+ data points for reliable patterns

3. **ML predictions work best with more data**:
   - Use 60-90 days for better ML accuracy

## 📚 **Documentation**

- **README.md**: Project overview and features
- **docs/**: Detailed documentation
- **CHANGELOG.md**: Version history and updates

## 🆘 **Support**

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Verify all dependencies are installed**: `pip list`
3. **Test with the demo**: `python cryptvault_cli.py --demo`
4. **Check data sources**: `python cryptvault_cli.py --status`

## 🎉 **Success!**

If you see beautiful ASCII charts with pattern analysis, you're all set! 

Example successful output:
```
                           Chart Analysis - BTC (1d)
126422.78 │ │       │    │  │ │       │     │  ││       │  │              ││   │
123539.81 │ │     *●│    │  │ │     *●│     │  ↘│    *● │ │││             │█   │
120656.83 │ │       /    │  │ │       //    │  ││       │▲▼▲▼█▲▼█▲▼█    │▲▲▼█│ │
[... beautiful ASCII candlestick chart with pattern overlays ...]

Detected Patterns:
────────────────────────────────────────────────────────────
 1. * Expanding Triangle        [Bilateral/Neutral] [██████████] 100.0% ●
 2. ↘ Bearish Divergence        [Divergence Pattern] [██████████] 100.0% ●
```

**Welcome to CryptVault! 🚀📊**